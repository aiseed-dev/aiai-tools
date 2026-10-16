# SPDX-License-Identifier: AGPL-3.0-or-later
"""python3 tenken/test_tenken.py   (standard library only, no network)"""
import datetime as dt
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import tenken  # noqa: E402

KEV = {"catalogVersion": "2026.10.16", "count": 3, "vulnerabilities": [
    {"cveID": "CVE-2026-0001", "vendorProject": "Cisco", "product": "IOS XE Software",
     "vulnerabilityName": "Cisco IOS XE Web UI Privilege Escalation", "dateAdded": "2026-10-15",
     "dueDate": "2026-11-05", "requiredAction": "Apply mitigations per vendor instructions.",
     "knownRansomwareCampaignUse": "Unknown"},
    {"cveID": "CVE-2026-0002", "vendorProject": "Fortinet", "product": "FortiOS",
     "vulnerabilityName": "Fortinet FortiOS SSL-VPN Heap Overflow", "dateAdded": "2026-10-01",
     "dueDate": "2026-10-22", "requiredAction": "Apply updates.", "knownRansomwareCampaignUse": "Known"},
    {"cveID": "CVE-2026-0003", "vendorProject": "", "product": "", "vulnerabilityName": "no names",
     "dateAdded": "2026-10-01"},
]}
NOW = dt.datetime(2026, 10, 16, 6, 0, tzinfo=tenken.JST)
JVN = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"
 xmlns:sec="http://jvn.jp/rss/mod_sec/3.0/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:status="http://jvndb.jvn.jp/myjvn/Status">
 <item rdf:about="https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000100.html">
  <title>ヤマハ製のルータにおける複数の脆弱性</title>
  <link>https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000100.html</link>
  <sec:identifier>JVNDB-2026-000100</sec:identifier>
  <sec:references source="CVE" id="CVE-2026-1111"/>
  <sec:cpe version="2.2" vendor="ヤマハ" product="RTX シリーズ">cpe:/h:yamaha:rtx</sec:cpe>
  <dcterms:issued>2026-10-15T12:00+09:00</dcterms:issued>
 </item>
 <item rdf:about="https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000101.html">
  <title>Linux の Linux Kernel における脆弱性</title>
  <link>https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000101.html</link>
  <sec:identifier>JVNDB-2026-000101</sec:identifier>
  <sec:cpe version="2.2" vendor="Linux" product="Linux Kernel">cpe:/o:linux:linux_kernel</sec:cpe>
  <dcterms:issued>2026-10-15T12:00+09:00</dcterms:issued>
 </item>
 <item rdf:about="https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000102.html">
  <title>Cisco IOS XE における脆弱性</title>
  <link>https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000102.html</link>
  <sec:identifier>JVNDB-2026-000102</sec:identifier>
  <sec:references source="CVE" id="CVE-2026-0001"/>
  <sec:cpe version="2.2" vendor="シスコシステムズ" product="IOS XE">cpe:/o:cisco:ios_xe</sec:cpe>
  <dcterms:issued>2026-10-15T12:00+09:00</dcterms:issued>
 </item>
 <status:Status version="3.3" retCd="0" errCd="" errMsg="" totalRes="3" totalResRet="3" firstRes="1"/>
</rdf:RDF>""".encode()


class Tenken(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.kev = os.path.join(self.dir, "kev.json")
        with open(self.kev, "w") as f:
            json.dump(KEV, f)

    def tearDown(self):
        self.tmp.cleanup()

    def kiki(self, rows):
        with open(os.path.join(self.dir, "kiki.csv"), "w", encoding="utf-8") as f:
            f.write("名前,メーカー,製品,版,記録\n" + "".join(",".join(r) + "\n" for r in rows))

    def log(self, name, hours_ago):
        path = os.path.join(self.dir, name)
        with open(path, "w") as f:
            f.write("x\n")
        t = (NOW - dt.timedelta(hours=hours_ago)).timestamp()
        os.utime(path, (t, t))
        return path

    def run_day(self, day="2026-10-16", **kw):
        return tenken.run(day, self.dir, self.kev, jvn=False, ai="none", now=NOW, **kw)

    def test_a_quiet_day_is_one_line(self):
        self.kiki([("本社のルーター", "Yamaha", "RTX1300", "Rev.23", self.log("rtx.log", 1))])
        report, text = self.run_day()
        self.assertEqual(report["当たった知らせ"], [])
        self.assertEqual(text.strip().splitlines()[-1], tenken.QUIET)
        self.assertEqual(len(text.strip().splitlines()), 3)  # title, blank, the line

    def test_old_entries_are_listed_once_then_only_counted(self):
        self.kiki([("VPN", "Fortinet", "FortiOS", "7.2", self.log("vpn.log", 1))])
        report, text = self.run_day("2026-10-16")  # FortiOS entry added 2026-10-01: old on the first check
        self.assertFalse(report["当たった知らせ"][0]["新しい"])
        self.assertIn("前から載っていて、初めて当たった知らせ", text)
        self.assertIn("CVE-2026-0002", text)
        report, text = self.run_day("2026-10-17")
        self.assertEqual(len(text.strip().splitlines()), 3)
        self.assertIn("前から知らせている物 1 件", text)
        self.assertNotIn("CVE-2026-0002", text)

    def test_maker_and_product_match_whatever_the_spelling(self):
        self.kiki([("境界", "cisco", "IOS-XE", "17.9", ""), ("VPN", "Fortinet", "FortiGate", "", "")])
        report, text = self.run_day()
        ids = [(h["機器"], h["id"]) for h in report["当たった知らせ"]]
        self.assertEqual(ids, [("境界", "CVE-2026-0001")])  # FortiGate is not FortiOS; empty names never match
        self.assertIn("https://nvd.nist.gov/vuln/detail/CVE-2026-0001", text)
        self.assertIn("版が当たるかは、知らせで確かめてください", text)

    def test_what_was_told_before_is_kept_apart_from_the_new(self):
        self.kiki([("境界", "Cisco", "IOS XE", "", "")])
        report, text = self.run_day("2026-10-15")  # added 2026-10-15: new
        self.assertTrue(report["当たった知らせ"][0]["新しい"])
        self.assertIn("新しく当たった知らせ", text)
        report, text = self.run_day("2026-10-16")  # told yesterday: no longer new
        self.assertFalse(report["当たった知らせ"][0]["新しい"])
        self.assertNotIn("新しく当たった知らせ", text)

    def test_a_log_that_stopped_or_is_missing_is_reported(self):
        self.kiki([("A", "Yamaha", "RTX830", "", self.log("a.log", 30)),
                   ("B", "Yamaha", "RTX830", "", os.path.join(self.dir, "none.log")),
                   ("C", "Yamaha", "RTX830", "", self.log("c.log", 2))])
        report, text = self.run_day()
        self.assertEqual([x["状態"] for x in report["記録"]], ["届いていない", "無い", "届いている"])
        self.assertNotIn(tenken.QUIET, text)
        self.assertIn("新しく当たる知らせはありません。", text)

    def test_a_notice_that_could_not_be_fetched_is_not_a_quiet_day(self):
        self.kiki([("A", "Yamaha", "RTX830", "", "")])
        report, text = tenken.run("2026-10-16", self.dir, os.path.join(self.dir, "x.json"), jvn=False,
                                  ai="none", now=NOW, fetcher=lambda url: (_ for _ in ()).throw(OSError("offline")))
        self.assertEqual(len(report["取れなかった知らせ"]), 1)
        self.assertIn("取れなかった知らせ", text)
        self.assertNotIn(tenken.QUIET, text)

    def test_the_ai_writes_at_most_8_lines_and_only_when_something_is_found(self):
        calls = []
        orig = tenken.ollama
        tenken.ollama = lambda prompt: calls.append(prompt) or "\n".join(f"{i} 行目" for i in range(12))
        try:
            self.kiki([("A", "Yamaha", "RTX830", "", self.log("a.log", 1))])
            tenken.run("2026-10-16", self.dir, self.kev, jvn=False, ai="ollama", now=NOW)
            self.assertEqual(calls, [])  # a quiet day asks nothing
            self.kiki([("境界", "Cisco", "IOS XE", "", "")])
            report, _ = tenken.run("2026-10-17", self.dir, self.kev, jvn=False, ai="ollama", now=NOW)
            self.assertEqual(len(report["所見"].splitlines()), 8)
            self.assertIn("CVE-2026-0001", calls[0])
        finally:
            tenken.ollama = orig

    def test_jvn_matches_japanese_maker_names_and_skips_what_cisa_already_told(self):
        urls = []
        fetch = lambda url: urls.append(url) or JVN
        self.kiki([("支店", "Yamaha|ヤマハ", "RTX830|RTX シリーズ", "", ""),
                   ("境界", "Cisco|シスコシステムズ", "IOS XE", "", "")])
        report, text = tenken.run("2026-10-16", self.dir, self.kev, jvn=True, ai="none", now=NOW, fetcher=fetch)
        got = sorted((h["機器"], h["出どころ"], h["id"]) for h in report["当たった知らせ"])
        self.assertEqual(got, [("境界", "CISA KEV", "CVE-2026-0001"), ("支店", "JVN", "JVNDB-2026-000100")])
        self.assertIn("https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000100.html", text)
        self.assertTrue(all("rangeDatePublic=n" in u and "rangeDateFirstPublished=n" in u for u in urls))
        self.assertEqual(len(urls), 3)  # once for each product name

    def test_a_list_without_the_needed_columns_stops(self):
        with open(os.path.join(self.dir, "kiki.csv"), "w", encoding="utf-8") as f:
            f.write("name,maker\nA,B\n")
        with self.assertRaises(ValueError):
            self.run_day()


if __name__ == "__main__":
    unittest.main()
