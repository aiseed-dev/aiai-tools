# このリポジトリで作業するときの決まり

aiai tools は「AI との協働ツール」です。詳しく言うときは「事業のための、AI との協働ツール」と言います。
会社や団体が、認証、コード、文書、メール、会議、API、社内の AI、データ分析、ERP を、
OSS と AI で自分の側に置くためのスキルを置くリポジトリです。個人と小さな店のための
[aiai](https://github.com/aiseed-dev/aiai) と同じ発注者の、別のリポジトリです。
書き方、確かめ方、作業の進め方は aiai の CLAUDE.md と同じで、ここには違う所と、この
リポジトリで決めたことだけを書きます。

## 方針(発注者が決めたこと)

- 土台は aiseed.dev の「AIネイティブな仕事の作法 — ソフトウェア開発編」の自立編
  (https://aiseed.dev/ai-native-ways/software/、CC BY 4.0)。順番もそれに合わせる。aiseed.dev の
  文と公式の説明書が違うときは、公式の説明書に合わせ、違いを README に書く
- もう、コードは要らない時代であることを強調する。コードを買う、書く人を雇う、持つ会社に頼む、の
  どれも要らない。値打ちは、何を作り、何を守り、どう確かめるかを会社の言葉で書いたスキルにある
- 中心はスキル(`SKILL.md`)。設定の見本(`compose.yaml`、`Caddyfile`)と `.py` は動く例で、
  作り直してよい。今あるファイルは消さない
- 置き換えは 1 つずつ、古い物と並べて動かし、確かめてから切り替える
- 認証は、自分で作るアプリの分を PocketBase に集め、社員のサインインは Apple ID と Google ID。
  Microsoft ID は移る間の選択肢とだけ書く。PocketBase は OpenID Connect の提供者にならないので、
  OSS の道具の認証はそれぞれが持つ(2026-09-28 に確かめた)
- 使う OSS は、OSI の認めたライセンスの物にする。Open WebUI と LobeChat は条件を足した
  ライセンスなので使わず、AI の画面は AnythingLLM(MIT)にする。VLM 監視(`kanshi/`)の
  モデルは、OSI でなくてよい。住宅で住人が使うのは商用でないので、問題は少ない。会社が空き家の
  見守りや管理の仕事として使うときは、商用で使えるかと、監視や顔認識を禁じる条項がないかを確かめる
  (2026-09-29 に決めた)
- コードの開発は Claude でよい。端末で動くコーディングエージェントを前提にしない。
  コードと設定は AI が下書きし、コマンドは会社の人が動かす
- 秘密の値は、AI への依頼にもリポジトリにも入れない。README に具体的に書く(API のトークンと鍵、
  パスワード入りの接続文字列、`.env`、compose に直に書いた秘密の値、SSH と TLS の秘密鍵、
  データベースのファイル)。見本には `変えてください`、`example.jp`、`127.0.0.1` と
  `.env.example` を使う。入ってしまったら、まず無効にして作り直す
- 社員やお客さんの個人の情報(他人の情報)は、学習に使わないと確かめたサービスか、自分の機械の
  AI でだけ扱う(個人情報保護委員会の注意喚起、2023-06-02)。会社の名前、住所、電話は事業として
  出す物なので、「渡さない」と決めつけない
- Web サイトは aiai の `website/` のスキルを使い、ここでは作り直さない。officework も aiai と
  同じく、公開された版を使うだけにする
- ERP は Tryton(8.0 LTS、PostgreSQL)にする(2026-10-12 に決めた)。全部がファイルに書かれ、
  日本の分を本体に手を入れずにモジュールとして置けるから。ERPNext は、設計を読む元として残す。
  ERP とは何かと、自分の PC で動かせる環境を作ることと、日本で使うための訳と会計のモジュールを書く。
  移るかどうかは、使えると分かってから考える。GPL と「自社利用限定」の関係は `erpnext/README.md`
  に書いてあり、法律の助言ではないと明記する

## 作業の進め方(aiai と違う所)

- 作業を始めるときに `python tools/kakunin.py --fetch` を動かす。`tools/kakunin.py` は aiai の物と
  同じスクリプトで、標準ライブラリだけで動く。直すときは aiai の側を直し、ここに写す
- ダウンロード(apt、docker pull、pip、conda、モデル)は、名前、出どころ、大きさを伝えて
  許しを得てからする。このリポジトリの中では、サーバーに入れて動かすことはしない
- Issue のラベルは「入れた記録」「提案」「新しい情報」。GitHub のリポジトリと
  ラベルは発注者が作る
- push は発注者がする。コミットまでで止める。コミットは触ったファイルだけを名前で指定する

## 中身

| 場所 | 中身 |
|---|---|
| `server/`、`dodai/`、`ninshou/`、`code/`、`bunsho/`、`mail/`、`kaigi/`、`web/`、`api/`、`jouhou/`、`ai/` | aiseed.dev の自立編の順のスキル。見本の設定と `api/sample/main.py` |
| `bunseki/` | 表のデータから予測する(Polars、scikit-learn、LightGBM、SHAP)。`yosoku.py` |
| `kaiin/`、`tsuuchi/`、`renraku/`、`honnin/`、`kagi/`、`minpaku/`、`kanshi/`、`kaiseki/`、`network/` | 事業用のアプリの部品(会員、通知、メッセージ、本人確認、鍵、民泊の受付、VLM 監視、解析、ネットワーク)。`kaiseki/` に解析の受け口(Python、SQLite)とページのスクリプトとテスト。`kaiseki/d1/` は先に作った Cloudflare D1 の広告の見本。認証は `ninshou/` に書き足した |
| `tryton/` | ERP とは何かと、Tryton 8.0 を自分の PC で動かす手順と、日本の会計(`account_jp`)の計画。`aiai_ja/` は Tryton の日本語(GPL-3.0-or-later、訳は `yaku.csv`、`tsukuru.py` で PO を作る、`trytond_import_ja` で読み込む) |
| `erpnext/` | ERPNext を自分の PC で動かした手順(設計を読む元)。`aiai_ja/` は訳の追加と修正の Frappe アプリ。`README.md` にライセンスの決まり |
| `packages/` | ほかのアプリでも使える部品のパッケージ(MIT、パッケージごとに PyPI に出す。タグは `<名前>-v<版>`)。`flet-gpumap` は weather の flet-gpufield が元。`nc4rs` は netcdf-rust を PyO3 でつないだ netCDF4 の代わり(試験は netCDF4 と比べる) |
| `tools/kakunin.py` | 出典の URL と確かめた日を集め、確かめ直す物を出す。aiai と同じ |
| `HOUKOKU.md`、`.github/ISSUE_TEMPLATE/` | 報告のしかたと Issue のひな形 |

## 残っていること(2026-09-28 時点)

- どのスキルも、まだサーバーに入れて動かしていない。手順と版は公式の説明書で確かめた
  (2026-09-28)。動かした人の報告で直す
- `api/sample/main.py` と `bunseki/yosoku.py` は py_compile だけ。部品(fastapi、polars、
  scikit-learn など)が入っていない。conda で入れて動かすには、発注者の許しが要る
- Cal.com の自分で置く版は cal.diy(MIT)に分かれ、「個人の、本番でない利用に強く勧める」と
  書いてある。使うかどうかは会社が決める形にした
- Tryton 8.0.11 は、この PC の `~/apps/tryton`(conda の環境は `.venv`、PostgreSQL 17 は apt)で、
  始めのウィザードの勘定科目まで動かした(2026-10-12)。販売から請求書までの 1 件は、まだ通していない。
  日本語の訳と日本の勘定科目、消費税のモジュールは、公式に無いので作る。最初の目標は個人事業の
  帳簿と青色申告決算書で、弥生と freee から移れるようにする(個人が開業するときに最初に覚えることだから)
- ERPNext は、Docker を使わずに(MariaDB 10.11、conda、bench)この PC で動かして確かめた
  (2026-10-06)。訳は `erpnext/aiai_ja/` で足して直す(用語集 `yougo.csv` にそろえる)。帳票の
  ひな形に英語が直に書かれた所は、日本の帳票を作るときに直す。Docker の見本は動かしていない。
  スターターの ja.csv の約 35% は ERPNext version-13 の翻訳(GPL-3.0)と同じで、出どころは作者に
  聞いていない
- ntfy は、VLM 監視と鍵のスキルに 1 行だけ添えた。サーバーへの置き方と、iPhone の上流
  (ntfy.sh)の設定は、時間ができたら足す(2026-10-06)
- `kaiseki/` は、analytics.aiseed.dev(deb2)で動き、天気のサイト weather.time-j.net で
  2026-10-07 に有効になった(実装と置き場所は「aiaiの管理者」、組み込みは「Weather アプリ開発」の
  セッション)。発注者の決めたこと: コードは aiai-tools に置く、まず ID だけ(会員とのひもづけはまだ)、
  数えるサイトは決めない。本番で「受け入れる」から消すまでと、タブを閉じたときの leave は、まだ
  確かめていない。広告の仕組みは、解析が動いてから「aiaiの管理者」が進める。先に作った Cloudflare
  の D1 版は、Cloudflare には出していない。置き場所は、天気のサイトの分を deb2 の公開サーバーで、aiai の
  分を Google Cloud で処理する(2026-10-08 に発注者が決めた)。ページのスクリプトの開発は aiai-tools でする
- GitHub のリポジトリ(aiseed-dev/aiai-tools、公開)は発注者が作る。作ったらラベルを作る
