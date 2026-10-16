# aiai tools

AI との協働ツール

事業のための、AI との協働ツールです。会社や団体が、自分たちの IT を AI と一緒に自分で持つための
スキルを置いています。
[aiai](https://github.com/aiseed-dev/aiai) が個人と小さな店のための物なのに対し、aiai tools は、認証、コード、文書、
メール、会議、API、社内の AI、データ分析、ERP のように、会社が外のサービスに預けている物を、
OSS と AI で自分の側に置くための物です。

土台にしたのは、aiseed.dev の「AIネイティブな仕事の作法 — ソフトウェア開発編」の自立編
(https://aiseed.dev/ai-native-ways/software/、CC BY 4.0)です。そこにある考え方
(閉じた形式と外に預けた鍵がロックインの元であること、1 つずつ順に置き換えること、
1 人と AI で運用すること)を、aiai の決まり(スキルが中心、出典と確かめた日を付ける、
本人が決める)で書き直しました。2026-09-28 に確かめました。

## もう、コードは要らない時代です

会社がコードを買う、コードを書く人を雇う、コードを持つ会社に頼む。そのどれも、要らなくなりました。
コードは、何を作るかが決まっていれば、AI がその場で書きます。書き直しも AI がします。
コードを持っていることには、もう値打ちがありません。

値打ちがあるのは、何を作り、何を守り、どう確かめるかを、会社の言葉で書いた物です。それがこの
リポジトリのスキル(`SKILL.md`)です。会社の人は、何を自分の側に置くか、誰が何を見てよいか、
古い物をいつ止めるかを決めます。AI は、それを読んで、設定とコードを書きます。

企業の基幹システムは、AI で扱いやすい物です。受注、在庫、請求の計算のように、仕事の決まりが
はっきりしていて、データも表の形にそろっています。AI は、決まりを読んでコードを書き直し、
古い仕組みと同じ入力で同じ答えが出るかを比べて確かめられます([api](api/))。ネットワークと
Web の構築も同じです。DNS、ファイアウォール、リバースプロキシ、HTTPS、静的なサイトは、
公式の説明書に決まった形があり、設定はテキストで書けて、つながるかどうかで確かめられます
([server](server/)、[web](web/))。手間がかかるのは、
むしろ事業用のアプリにいつも出てくる部品(認証、本人確認、顔認識、メッセージ)です。法令と
他人の情報が絡むので、決まりを条文で確かめることが値打ちになります。

このリポジトリにあるコードと設定は、動く例です。写して使う物ではなく、会社の AI がスキルを
読んで作り直す物です。土台にした aiseed.dev の導入編は、AI が最も難しいコーディングの問題を
解くこと、ソフトウェアエンジニアの仕事を AI がすること、人の役割は何を作るかを決める
ビルダーになることを書いています(https://aiseed.dev/ai-native-ways/software/、CC BY 4.0、
2026-09-28 に確かめました)。

## 考え方

- 中心はスキル(`SKILL.md`)です。何を入れるか、何を守るか、どう確かめるかを書き、設定や
  プログラムは、会社の AI がその会社に合わせて作ります。動く例として置いた設定ファイルは、
  作り直してかまいません
- 置き換えは 1 つずつ、古い物と並べて動かし、確かめてから切り替えます。全部を一度に
  替えません
- 認証は 1 か所で持ち、何ができるかは道具ごとに決めます。自分で作るアプリの認証は
  PocketBase に集め、社員のサインインは Apple ID か Google ID でします。aiai と同じ理由で、
  Microsoft ID は足しません(認証の相手を 1 つ足すたびに、登録して手入れする所が 1 つ増えます)
- 外のサービスに頼るのは、大きな AI のモデルと、Web サイトの公開(Cloudflare Pages)と、
  メールの中継くらいにします。それ以外は OSS を自分のサーバーで動かします
- 秘密の値は、AI への依頼にも、このリポジトリにも、会社のリポジトリ([code](code/))にも
  入れません。具体的には、API のトークンと鍵(AWS のアクセスキー、Google Cloud のサービス
  アカウントの JSON の鍵、Cloudflare の API トークン、Apple のサインインの鍵 `.p8`、AI の
  API キー)、パスワードが入った接続文字列(`postgresql://ユーザー:パスワード@ホスト/…`)、
  `.env` のファイル、compose に直に書いた `JWT_SECRET` や `POSTGRES_PASSWORD`、SSH と TLS の
  秘密鍵、社員やお客さんのデータベースのファイルです。1 度 push すると、消しても漏れた物として
  扱い、まず無効にして作り直します。GitHub の個人のアカウントには push の前に止める機能
  (push protection)が最初から有効ですが、止められる物は一部です。Forgejo にはこの機能が
  あるかを確かめていません(GitHub Docs「Push protection」
  https://docs.github.com/en/code-security/concepts/secret-security/push-protection 、2026-09-28 に確かめました)
- 社員やお客さんの個人の情報は、学習に使わないと確かめた AI のサービスか、自分の機械の AI
  ([ai](ai/))でだけ扱います。会社の名前、住所、電話は AI に渡してかまいません(個人情報保護
  委員会の注意喚起 https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/ 、
  2026-09-28 に確かめました)
- ライセンスを確かめてから入れます。確かめた版とライセンスは [使う物](TSUKAUMONO.md) に書いています

## 順番

aiseed.dev の自立編の順です。1 つ終わってから次に進みます。

| 順 | フォルダー | 入れる物 | 置き換える物 |
|---|---|---|---|
| 0 | [server](server/) | サーバー、Docker、Caddy、DNS、バックアップ | (すべての土台) |
| 1 | [dodai](dodai/) | SQLite、PostgreSQL + pgvector、DuckDB、Polars | Azure SQL、Cloud SQL、Power BI |
| 2 | [ninshou](ninshou/) | PocketBase | Entra ID、Google ID |
| 3 | [code](code/) | Forgejo | GitHub、SharePoint、Drive |
| 4 | [bunsho](bunsho/) | OnlyOffice Docs | Office、Docs/Sheets/Slides |
| 5 | [mail](mail/) | Stalwart | Exchange/Outlook、Gmail |
| 6 | [kaigi](kaigi/) | Jitsi Meet、Cal.diy、BigBlueButton、Radicale | Teams、Meet、Bookings |
| 7 | [web](web/) | Cloudflare Pages(aiai の `website/` と cf-publish) | WordPress、Power Pages |
| 8 | [api](api/) | FastAPI(認証は PocketBase、データは PostgreSQL) | Power Apps、Apps Script、古い基幹の仕組み |
| 9 | [jouhou](jouhou/) | OCR、分類、Markdown や adoc への書き起こし | (AI の前の整備) |
| 10 | [ai](ai/) | Ollama、AnythingLLM、pgvector で RAG | Copilot、Gemini |
| 11 | [bunseki](bunseki/) | Polars、scikit-learn、LightGBM、SHAP | 表のデータから予測する SaaS |
| 12 | [tryton](tryton/) | ERP とは何かを知り、Tryton を自分の PC で動かし、日本の訳と会計を足す | (使えると分かってから考える) |
|  | [erpnext](erpnext/) | ERPNext を自分の PC で動かした記録。Tryton に移すときに設計を読む元 | |

## 事業用のアプリの部品

事業用のアプリにいつも出てくる部品です。aiseed.dev の自立編にはない物で、順番はありません。
要る物から使います。認証は [ninshou](ninshou/) の「会員(お客さん)のサインイン」です。

| フォルダー | 中身 | 使う物 |
|---|---|---|
| [kaiin](kaiin/) | 会員を集めて預かる(招待、同意、本人が見て消せる、漏えいの報告) | aiai の soudan、PocketBase |
| [tsuuchi](tsuuchi/) | 通知(取引のメールと Web Push。広告は入れない) | Stalwart、pywebpush |
| [renraku](renraku/) | メッセージ(会社と会員。会員どうしは届出が要ることがある) | PocketBase |
| [honnin](honnin/) | 本人確認(民泊と簡易宿所の宿泊者名簿が中心) | PocketBase、Jitsi |
| [kagi](kagi/) | 鍵(スマートロックで期間を決めた鍵を出して消す) | Matter と Home Assistant、各社の API |
| [minpaku](minpaku/) | 民泊の受付(受付番号、名簿と顔・身分証、経営者の承認、鍵、偶数月の定期報告。honnin と kagi をつなぐ) | Flet、追記だけの台帳 |
| [kanshi](kanshi/) | 住宅と空き家の VLM 監視と顔認識 | Frigate、Ollama、OpenCV Zoo |
| [kaiseki](kaiseki/) | 解析を自分のサーバーで(Google Analytics と同じ程度。ID は受け入れた人だけで、自分のサイトどうしで引き継ぎ、会員とひもづける。関心は集計と決まりで出す) | Python の標準ライブラリと SQLite |
| [network](network/) | Linux の PC をルーターにする | systemd-networkd、nftables、dnsmasq、Unbound、WireGuard、hostapd |
| [router](router/) | 会社のルーターを選び(記録を送れるかが第一)、区画ごとに止められる形に組み、記録を別の機械に置く | syslog(rsyslog)、WireGuard |
| [tenken](tenken/) | 毎朝、機器に当たる弱点の知らせ(CISA、JVN)と、記録が届いているかを知らせるアプリ | Python の標準ライブラリ、systemd の timer |

部品は、次のようにつながります。各フォルダーの `README.md` に、何ができるか、誰が使うか、何を
決めるかを書いています(`SKILL.md` は AI が読む物です)。

- 会員制のサービス(aiai の会員の例): 会員登録([kaiin](kaiin/))→ サインイン([ninshou](ninshou/))
  → 知らせ([tsuuchi](tsuuchi/))→ 問い合わせ([renraku](renraku/))→ 見たページの記録
  ([kaiseki](kaiseki/))
- 民泊: 予約と受付([minpaku](minpaku/))→ 本人確認と宿泊者名簿([honnin](honnin/))→ 鍵
  ([kagi](kagi/))→ 知らせ([tsuuchi](tsuuchi/))
- 会社のネットワーク: ルーターを選んで組み、記録を置く([router](router/))→ Linux の箱にするなら
  ([network](network/))→ 毎日の点検([tenken](tenken/))
- 家と建物: ネットワーク([network](network/))→ 見守り([kanshi](kanshi/))→ 知らせ
  ([tsuuchi](tsuuchi/))

## 使い方

1. このリポジトリを手元に取り、スキルを読める AI を用意します。Web サイト([web](web/))は
   [aiai](https://github.com/aiseed-dev/aiai) の `website/` のスキルを使うので、aiai も取ります

   ```
   git clone https://github.com/aiseed-dev/aiai-tools.git
   ```

2. `server/SKILL.md` から順に AI に読ませます。コードと設定は AI が下書きし、コマンドは会社の人が
   動かします。見本の設定(`compose.yaml`、`Caddyfile`、`.env.example`)は写して直します
3. 入れた物、困ったこと、変わっていたことは、[報告のしかた](HOUKOKU.md)で知らせてください

## いまの状態

手順と設定は公式の説明書で確かめた物で、多くはサーバーに入れて動かしてはいません。動かして
確かめたのは、ERPNext(2026-10-06、[erpnext](erpnext/))と、解析(2026-10-07、[kaiseki](kaiseki/)。
analytics.aiseed.dev で動き、天気のサイト weather.time-j.net で使っています)です。動かした人の
報告で直します。

## ライセンス

コード(`.py`、`.js`、`.css`、`.toml`)は AGPL-3.0-or-later(全文は [COPYING](COPYING))、それ以外(文書、
設定の見本、画像)は CC BY 4.0 です。詳しくは [LICENSE](LICENSE) にあります。Tryton の日本語の訳([tryton/aiai_ja](tryton/aiai_ja/))は、Tryton と同じ GPL-3.0-or-later です。[packages/](packages/) のパッケージは、ほかのアプリでも使えるように MIT です。aiai と同じ決まりです。aiseed.dev の文章(CC BY 4.0)を元にした所は、この README と各フォルダーの
`SKILL.md` に出典を書いています。
