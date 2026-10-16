# SPDX-License-Identifier: AGPL-3.0-or-later
"""The daily check of a company's network devices (standard library only).

    python3 tenken.py [--date YYYY-MM-DD]

Runs on the log machine every morning. It reads the device list (kiki.csv),
fetches the public notices of exploited and published weaknesses (CISA KEV,
JVN), matches them by maker and product, checks that each device's log file
grew in the last 24 hours, and writes one report a day (.adoc and .json).
It never connects to the devices. The AI, when used, only reads and writes.

Settings (environment):
  TENKEN_DIR       the folder for kiki.csv and the reports (default ~/tenken)
  TENKEN_MAILTO    send the report to this address through localhost:25
  TENKEN_AI        gemini (Vertex AI, with the VM's service account), ollama, or none (default)
  TENKEN_GEMINI_LOCATION, TENKEN_GEMINI_MODEL, TENKEN_OLLAMA_URL, TENKEN_OLLAMA_MODEL
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import smtplib
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage

JST = dt.timezone(dt.timedelta(hours=9))
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_PAGE = "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
NVD = "https://nvd.nist.gov/vuln/detail/"
JVN_API = "https://jvndb.jvn.jp/myjvn"
UA = "tenken/0.1 (+https://github.com/aiseed-dev/aiai-tools)"
QUIET = "新しく当たる知らせはありません。記録は全部届いています。"
COLUMNS = ("名前", "メーカー", "製品", "版", "記録")


def norm(s):
    """Lower case, letters and digits only (any script): "Cisco IOS XE" -> "ciscoiosxe" """
    return re.sub(r"[\W_]+", "", (s or "").lower())


def names(cell):
    """A cell of kiki.csv may hold several names: "Yamaha|ヤマハ" """
    return [n.strip() for n in (cell or "").split("|") if n.strip()]


def read_kiki(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in COLUMNS[:3] if rows and c not in rows[0]]
    if missing:
        raise ValueError(f"kiki.csv に列がありません: {', '.join(missing)}")
    return [{c: (r.get(c) or "").strip() for c in COLUMNS} for r in rows if (r.get("名前") or "").strip()]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def same(cell, b):
    """One of the names in the cell and b contain one another, after norm(); empty never matches."""
    b = norm(b)
    return bool(b) and any(a and (a in b or b in a) for a in map(norm, names(cell)))


def match_kev(kev, devices):
    """[(device, entry)] for KEV entries whose vendor and product match a device."""
    hits = []
    for d in devices:
        for v in kev.get("vulnerabilities", []):
            if same(d["メーカー"], v.get("vendorProject")) and same(d["製品"], v.get("product")):
                hits.append({
                    "機器": d["名前"], "版": d["版"], "出どころ": "CISA KEV",
                    "id": v.get("cveID", ""), "名前": v.get("vulnerabilityName", ""),
                    "載った日": v.get("dateAdded", ""), "期限": v.get("dueDate", ""),
                    "ランサムウェア": v.get("knownRansomwareCampaignUse", ""),
                    "すること": v.get("requiredAction", ""),
                    "出典": [KEV_PAGE, NVD + v.get("cveID", "")],
                })
    return hits


NS = {"rss": "http://purl.org/rss/1.0/", "sec": "http://jvn.jp/rss/mod_sec/3.0/",
      "dcterms": "http://purl.org/dc/terms/", "status": "http://jvndb.jvn.jp/myjvn/Status"}


def jvn_url(product, since):
    y, m, d = since.split("-")
    # All three ranges default to the past week, so each is set to n (no range)
    q = {"method": "getVulnOverviewList", "feed": "hnd", "lang": "ja", "keyword": product,
         "rangeDatePublic": "n", "rangeDateFirstPublished": "n",
         "rangeDatePublished": "n", "datePublishedStartY": y, "datePublishedStartM": m,
         "datePublishedStartD": d, "maxCountItem": "50"}
    return JVN_API + "?" + urllib.parse.urlencode(q)


def in_title(cell, title):
    return any(norm(n) and norm(n) in norm(title) for n in names(cell))


def match_jvn(devices, since, fetcher=fetch):
    """JVN iPedia entries published since `since` whose maker and product match a device.

    JVN writes makers in Japanese (ヤマハ) and products in groups (RT シリーズ), so a
    device matches through the names in its cell, in the CPE or in the title."""
    hits, got = [], set()
    for d in devices:
        for product in names(d["製品"]):
            root = ET.fromstring(fetcher(jvn_url(product, since)))
            st = root.find("status:Status", NS)
            if st is not None and st.get("retCd") not in (None, "0"):
                raise RuntimeError(f"MyJVN: {st.get('errCd')} {st.get('errMsg')}")
            for it in root.findall("rss:item", NS):
                jid = it.findtext("sec:identifier", "", NS)
                title = it.findtext("rss:title", "", NS)
                cpes = it.findall("sec:cpe", NS)
                if not jid or (d["名前"], jid) in got:
                    continue
                if not (any(same(d["メーカー"], c.get("vendor")) for c in cpes) or in_title(d["メーカー"], title)):
                    continue
                if not (any(same(d["製品"], c.get("product")) for c in cpes) or in_title(d["製品"], title)):
                    continue
                got.add((d["名前"], jid))
                cves = [r.get("id") for r in it.findall("sec:references", NS) if r.get("source") == "CVE"]
                hits.append({
                    "機器": d["名前"], "版": d["版"], "出どころ": "JVN", "id": jid, "名前": title,
                    "CVE": cves, "載った日": (it.findtext("dcterms:issued", "", NS) or "")[:10],
                    "期限": "", "すること": "", "出典": [it.findtext("rss:link", "", NS)] + [NVD + c for c in cves],
                })
    return hits


def log_status(devices, now):
    """For each device with a log file: 届いている / 届いていない / 無い."""
    out = []
    for d in devices:
        path = d["記録"]
        if not path:
            continue
        try:
            mtime = dt.datetime.fromtimestamp(os.stat(path).st_mtime, JST)
        except OSError:
            out.append({"機器": d["名前"], "記録": path, "状態": "無い", "最後": ""})
            continue
        ok = now - mtime <= dt.timedelta(hours=24)
        out.append({"機器": d["名前"], "記録": path, "状態": "届いている" if ok else "届いていない",
                    "最後": mtime.isoformat(timespec="minutes")})
    return out


def known_ids(folder, today):
    """(IDs already told on earlier days, the day of the last report or "")"""
    ids, last = set(), ""
    for name in sorted(os.listdir(folder)):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", name) and name[:10] < today:
            try:
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    for h in json.load(f).get("当たった知らせ", []):
                        ids.add((h["機器"], h["id"]))
                last = name[:10]
            except (OSError, ValueError, KeyError):
                continue
    return ids, last


def ai_comment(report, kind):
    if kind in ("", "none"):
        return ""
    facts = {k: report[k] for k in ("日", "当たった知らせ", "記録", "取れなかった知らせ")}
    prompt = ("会社のネットワークの機器の、今朝の点検の結果です。急ぐ順と、担当の人がすることを、"
              "日本語の普通の説明文で 8 行以内で書いてください。結果に無いことは書かないでください。\n\n"
              + json.dumps(facts, ensure_ascii=False, indent=1))
    try:
        text = gemini(prompt) if kind == "gemini" else ollama(prompt)
    except Exception as e:  # the report goes out without the comment
        return f"(AI の所見は書けませんでした: {type(e).__name__})"
    return "\n".join(text.strip().splitlines()[:8])


def _post_json(url, body, headers=None, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def gemini(prompt):
    # The VM's service account, through the metadata server: no key on the machine
    md = "http://metadata.google.internal/computeMetadata/v1/"
    get = lambda p: urllib.request.urlopen(urllib.request.Request(md + p, headers={"Metadata-Flavor": "Google"}), timeout=10).read().decode()
    token = json.loads(get("instance/service-accounts/default/token"))["access_token"]
    project = get("project/project-id")
    loc = os.environ.get("TENKEN_GEMINI_LOCATION", "asia-northeast1")
    model = os.environ.get("TENKEN_GEMINI_MODEL", "gemini-2.5-flash")
    url = (f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project}/locations/{loc}"
           f"/publishers/google/models/{model}:generateContent")
    r = _post_json(url, {"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
                   {"Authorization": f"Bearer {token}"})
    return "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])


def ollama(prompt):
    url = os.environ.get("TENKEN_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
    model = os.environ.get("TENKEN_OLLAMA_MODEL", "qwen3:8b")
    return _post_json(url, {"model": model, "prompt": prompt, "stream": False})["response"]


def is_quiet(report):
    # Entries known before are counted in the one line, not listed every morning
    return not any(h["初めて"] for h in report["当たった知らせ"]) and not report["取れなかった知らせ"] and all(
        x["状態"] == "届いている" for x in report["記録"])


def quiet_line(r):
    old = len(r["当たった知らせ"])
    if not old:
        return QUIET
    return f"新しく当たる知らせはありません(前から知らせている物 {old} 件。一覧は json にあります)。記録は全部届いています。"


def to_adoc(r):
    if is_quiet(r):
        return f"= {r['日']} の点検\n\n{quiet_line(r)}\n"
    out = [f"= {r['日']} の点検", ""]
    if r["所見"]:
        out += ["== AI の所見", "", r["所見"], ""]
    new = [h for h in r["当たった知らせ"] if h["新しい"]]
    first = [h for h in r["当たった知らせ"] if h["初めて"] and not h["新しい"]]
    old = [h for h in r["当たった知らせ"] if not h["初めて"]]
    if new:
        out += ["== 新しく当たった知らせ", ""]
        for h in new:
            ver = f"(版 {h['版']})" if h["版"] else "(版は一覧に無い)"
            out.append(f"* {h['機器']}{ver}: {h['id']} {h['名前']}")
            if h.get("載った日"):
                due = f"、対応の期限(米国の官庁向け) {h['期限']}" if h.get("期限") else ""
                out.append(f"  ** {h['出どころ']} に載った日 {h['載った日']}{due}")
            if h.get("すること"):
                out.append(f"  ** すること(知らせの文のまま): {h['すること']}")
            out.append("  ** 当たるのはメーカーと製品の名前までです。版が当たるかは、知らせで確かめてください")
            out.append("  ** 出典: " + "、".join(h["出典"]))
        out.append("")
    if first:
        out += ["== 前から載っていて、初めて当たった知らせ(1 度だけ並べます)", ""]
        out += [f"* {h['機器']}: {h['id']}({h.get('載った日', '')}) {h['名前']} {h['出典'][-1]}" for h in first]
        out.append("")
    if old:
        out += [f"前から知らせている物が {len(old)} 件あります(一覧は json にあります)。", ""]
    if r["取れなかった知らせ"]:
        out += ["== 取れなかった知らせ", ""] + [f"* {x}" for x in r["取れなかった知らせ"]] + [""]
    if r["記録"]:
        out += ["== 記録が届いているか", ""]
        out += [f"* {x['機器']}: {x['状態']}" + (f"(最後 {x['最後']})" if x["最後"] else "") for x in r["記録"]]
        out.append("")
    if not new and not r["取れなかった知らせ"]:
        out.insert(2, "新しく当たる知らせはありません。\n")
    return "\n".join(out)


def mail(text, day, to):
    m = EmailMessage()
    m["Subject"] = f"{day} のネットワークの機器の点検"
    m["From"] = f"tenken@{os.uname().nodename}"
    m["To"] = to
    m.set_content(text)
    with smtplib.SMTP("localhost", 25, timeout=30) as s:
        s.send_message(m)


def run(day, folder, kev_source=None, jvn=True, ai=None, now=None, fetcher=fetch):
    now = now or dt.datetime.now(JST)
    devices = read_kiki(os.path.join(folder, "kiki.csv"))
    errors, hits = [], []
    try:
        if kev_source and os.path.exists(kev_source):
            with open(kev_source, "rb") as f:
                raw = f.read()
        else:
            raw = fetcher(kev_source or KEV_URL)
        hits += match_kev(json.loads(raw), devices)
    except Exception as e:
        errors.append(f"CISA KEV: {type(e).__name__}: {e}")
    if jvn:
        try:
            since = (dt.date.fromisoformat(day) - dt.timedelta(days=30)).isoformat()
            kev = {(h["機器"], h["id"]) for h in hits}
            # A JVN entry for a CVE already on the CISA list for the device is told once, by CISA
            hits += [h for h in match_jvn(devices, since, fetcher)
                     if not any((h["機器"], c) in kev for c in h["CVE"])]
        except Exception as e:
            errors.append(f"JVN: {type(e).__name__}: {e}")
    seen, last = known_ids(folder, day)
    # New: put on the list since the last report (on the first check, in the last 7 days)
    since = last or (dt.date.fromisoformat(day) - dt.timedelta(days=7)).isoformat()
    for h in hits:
        h["初めて"] = (h["機器"], h["id"]) not in seen
        h["新しい"] = h["初めて"] and h.get("載った日", "") >= since
    hits.sort(key=lambda h: (h["新しい"], h["初めて"], h.get("載った日", "")), reverse=True)
    report = {"日": day, "機器の数": len(devices), "当たった知らせ": hits,
              "取れなかった知らせ": errors, "記録": log_status(devices, now), "所見": ""}
    if not is_quiet(report):
        report["所見"] = ai_comment(report, ai if ai is not None else os.environ.get("TENKEN_AI", "none"))
    with open(os.path.join(folder, f"{day}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    text = to_adoc(report)
    with open(os.path.join(folder, f"{day}.adoc"), "w", encoding="utf-8") as f:
        f.write(text)
    return report, text


def main(argv=None):
    p = argparse.ArgumentParser(description="ネットワークの機器の毎日の点検")
    p.add_argument("--date", default=dt.datetime.now(JST).date().isoformat())
    p.add_argument("--dir", default=os.environ.get("TENKEN_DIR", os.path.expanduser("~/tenken")))
    p.add_argument("--kev", help="CISA KEV の JSON(ファイルか URL。既定は CISA の URL)")
    p.add_argument("--no-jvn", action="store_true")
    a = p.parse_args(argv)
    _, text = run(a.date, a.dir, a.kev, not a.no_jvn)
    to = os.environ.get("TENKEN_MAILTO")
    if to:
        mail(text, a.date, to)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
