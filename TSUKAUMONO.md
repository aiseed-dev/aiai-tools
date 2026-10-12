# 使う物

aiai tools のスキルで使う物の、確かめた版とライセンスです。

2026-09-28 に、各プロジェクトの公開の場所(GitHub、Codeberg、Docker Hub、公式の説明書)で
確かめました。版は、そのときの最新の物です。制度と同じで、版もライセンスも変わるので、
入れる前に確かめ直してください。

| 物 | 確かめた版 | ライセンス | 出典 |
|---|---|---|---|
| Docker Engine | (Ubuntu 22.04、24.04、26.04 LTS 用) | Apache-2.0 | https://docs.docker.com/engine/install/ubuntu/ |
| Caddy | v2.11.4 | Apache-2.0 | https://github.com/caddyserver/caddy/releases |
| PostgreSQL + pgvector | pgvector v0.8.6、画像 `pgvector/pgvector:pg18` まで | PostgreSQL License | https://github.com/pgvector/pgvector |
| DuckDB | v1.5.5 | MIT | https://github.com/duckdb/duckdb |
| Polars | py-1.44.2 | MIT | https://github.com/pola-rs/polars |
| PocketBase | v0.40.4 | MIT | https://github.com/pocketbase/pocketbase/releases |
| Forgejo | v16.0.5 | GPL-3.0 | https://codeberg.org/forgejo/forgejo/releases |
| ONLYOFFICE Docs | v9.4.0 | AGPL-3.0 | https://github.com/ONLYOFFICE/DocumentServer/releases |
| Stalwart | v0.16.24 | AGPL-3.0(独自の SELv2 との二重) | https://github.com/stalwartlabs/stalwart/releases |
| Jitsi Meet(docker-jitsi-meet) | stable-11248 | Apache-2.0 | https://github.com/jitsi/docker-jitsi-meet/releases |
| Cal.diy | (calcom/cal.diy) | MIT | https://github.com/calcom/cal.diy |
| BigBlueButton | v3.0.37 | LGPL-3.0 | https://github.com/bigbluebutton/bigbluebutton/releases |
| Radicale | (Kozea/Radicale) | GPL-3.0 | https://github.com/Kozea/Radicale |
| FastAPI | (fastapi/fastapi) | MIT | https://github.com/fastapi/fastapi |
| Tesseract、OCRmyPDF | (tesseract-ocr/tesseract、ocrmypdf/OCRmyPDF) | Apache-2.0、MPL-2.0 | https://github.com/tesseract-ocr/tesseract 、https://github.com/ocrmypdf/OCRmyPDF |
| Ollama | v0.34.4 | MIT | https://github.com/ollama/ollama/releases |
| AnythingLLM | v1.16.2 | MIT | https://github.com/Mintplex-Labs/anything-llm/releases |
| North Mini Code 1.0(Cohere) | 30B(3B が動く)MoE | Apache-2.0 | https://docs.cohere.com/docs/north-mini-code-1.0 |
| scikit-learn、LightGBM、SHAP | 1.9.1、4.7.0、0.52.0(conda-forge) | BSD-3-Clause、MIT、MIT | https://anaconda.org/conda-forge/ |
| Tryton(trytond と各モジュール) | 8.0 LTS(8.0.11) | GPL-3.0-or-later | https://pypi.org/project/trytond/ 、https://www.tryton.org/download |
| sao(Tryton の Web の画面) | 8.0.12 | GPL-3.0-or-later | https://downloads.tryton.org/8.0/ |
| PostgreSQL(Tryton の DB、Debian 13 の物) | 17 | PostgreSQL License | https://packages.debian.org/trixie/postgresql |
| ERPNext、Frappe Framework | v16.36.1、v16.35.0(2026-10-06 にこの組で動かした) | GPL-3.0、MIT | https://github.com/frappe/erpnext/releases 、https://github.com/frappe/frappe/releases |
| frappe-bench(ERPNext を組んで動かす道具) | 5.31.0 | GPL-3.0 | https://pypi.org/project/frappe-bench/ |
| MariaDB(ERPNext の DB、Ubuntu 24.04 の物) | 10.11.14 | GPL-2.0 | https://packages.ubuntu.com/noble/mariadb-server |
| Redis(ERPNext のキュー、conda-forge の redis-server) | 7.2.11 | BSD-3-Clause | https://anaconda.org/conda-forge/redis-server |
| wkhtmltopdf(ERPNext の PDF) | 0.12.6.1-3 | LGPL-3.0 | https://github.com/wkhtmltopdf/packaging/releases |
| erpnext-ja-starter(ERPNext の日本語) | コミット b494234(2026-04-25) | MIT | https://github.com/maihatch/erpnext-ja-starter |
| aiai_ja(このリポジトリの ERPNext の訳の追加と修正) | 0.1.0 | AGPL-3.0-or-later、訳は CC BY 4.0 | [erpnext/aiai_ja](erpnext/aiai_ja/) |
| frappe_docker(Docker で動かす見本だけに使う) | v3.2.2 | MIT | https://github.com/frappe/frappe_docker/releases |
| Noto CJK(fonts-noto-cjk、PDF の日本語) | Ubuntu と Debian の物 | OFL-1.1 | https://packages.debian.org/bookworm/fonts-noto-cjk |
| pywebpush | 2.5.0 | MPL-2.0 | https://pypi.org/project/pywebpush/ |
| ntfy | v2.28.0 | Apache-2.0 と GPL-2.0 | https://github.com/binwiederhier/ntfy |
| Home Assistant | 2026.9.4 | Apache-2.0 | https://github.com/home-assistant/core |
| Frigate | v0.18.0 | MIT | https://github.com/blakeblackshear/frigate |
| OpenCV Zoo の YuNet、SFace | (opencv/opencv_zoo) | MIT、Apache-2.0 | https://github.com/opencv/opencv_zoo |
| nftables、systemd | 1.1.7、v262 | GPL、LGPL-2.1 | https://www.netfilter.org/projects/nftables/ 、https://github.com/systemd/systemd |
| dnsmasq、Unbound | 2.93、1.26.1 | GPL、BSD-3-Clause | https://thekelleys.org.uk/dnsmasq/doc.html 、https://github.com/NLnetLabs/unbound |
| WireGuard(wireguard-tools)、hostapd | v1.0.20260223、2.12 | GPL-2.0、BSD | https://www.wireguard.com/install/ 、https://w1.fi/hostapd/ |

BigBlueButton のライセンスは、リポジトリの LICENSE を GitHub の API で確かめました。

ERPNext の画像に入っている Frappe の版は、画像の由来の記録(provenance)の `FRAPPE_BRANCH` で
確かめました。ERPNext v16.36.1 の `pyproject.toml` は、Frappe に `>=16.21.0,<17.0.0` を求めています
(https://github.com/frappe/erpnext/blob/v16.36.1/pyproject.toml 、2026-09-29 に確かめました)。
