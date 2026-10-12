---
name: aiai-tools-tryton
description: ERP とは何かを伝え、Tryton(GPL-3.0 の OSS の ERP)の 8.0 LTS を、自分の PC(Debian)で PostgreSQL と conda の環境で、Docker を使わずに動かすのを手伝う。日本で使うために足す物(個人事業の帳簿と青色申告決算書、弥生と freee からの移行、日本語の訳、消費税)を、本体に手を入れずに、ファイルに書いたモジュールとして作る。
---

# Tryton を自分の PC で動かす

あなたは、この会社の人が ERP とは何かを知り、Tryton を自分の PC で動かして触れるように
するのを手伝います。専門の言葉は、初めて出るときに 1 度説明してください。

## 守ること

- 秘密の値(パスワード)を、会話にも、リポジトリにも書きません。管理者のパスワードは、会社の人が
  端末で打ち込みます
- ダウンロードの前に、名前、出どころ、大きさを伝えて許しを得ます
- `sudo` が要るコマンド(PostgreSQL を入れる)は、会社の人が動かします
- 会社の取引のデータを AI への依頼に貼りません
- 本体のモジュールは直しません。日本の分は、別のモジュールに書きます

## ERP とは何か

ERP は、会社の仕事(売る、買う、在庫、会計、人)を 1 つのデータベースで扱うソフトです。
仕事ごとに別の表やソフトを使うと、同じことを何度も入力し、数が合わなくなります。ERP では、
1 つの出来事を 1 度だけ入れ、次の書類はそこから作ります。Tryton の例です。

- 売る: 販売(Sale)を、下書き(Draft)→ 見積(Quotation)→ 確定(Confirmed)と進めると、
  出荷(Shipment)と請求書(Invoice)ができます。販売は、処理中(Processing)を経て、
  済み(Done)になります
- 請求書は、下書き → 確認済み(Validated)→ 記帳済み(Posted)→ 支払済み(Paid)と進みます。
  記帳すると、売掛金と売上と税の仕訳(Move)ができます。記帳した物は書き換えず、打ち消す
  請求書で直します
- 買う、在庫、会計、生産、プロジェクトも、同じ形でつながっています

これを、動かした環境で実際に 1 件通して見るのが、いちばん早く分かります(手順 6)。

## Tryton にした理由

- モデル、画面、権限、データが、全部ファイル(Python と XML)に書かれます。AI が書いた物が
  そのままリポジトリに入り、読み返せて、差分が見えます
- 本体のモデルを受け継いで、項目を足す、動きを変える書き方が 1 つに決まっています。日本の分を、
  本体に手を入れずに、別のモジュールに置けます
- 全部のモジュールが同じ版で出ます。前の版からの移行は、公式が対応しています

ERPNext([erpnext](../erpnext/))は、設計を読む元として置いておきます。

## 組み合わせ(2026-10-12 に配布元で確かめ、この PC で動かした)

| 物 | 版 | ライセンス |
|---|---|---|
| Tryton(trytond と各モジュール) | 8.0 LTS(8.0.11、2026-10-01) | GPL-3.0-or-later |
| sao(Web の画面) | 8.0.12 | GPL-3.0-or-later |
| PostgreSQL(Debian 13 の物) | 17 | PostgreSQL License |
| Python(conda-forge) | 3.13 | PSF |

8.0 は長期の支援版で、支援は 5 年です。ふつうの版は 6 か月ごとに出て、支援は 1 年です。
Tryton が使えるデータベースは PostgreSQL と SQLite だけで、MariaDB は使えません。

## 置き場所

開発する物(`~/dev` の下)と、動かす物を分けます。動かす物は `~/apps/tryton` にまとめます。

```
~/apps/tryton/
  .venv/          conda の環境(Tryton 本体)
  trytond.conf    設定
  sao/            画面
  files/          添付ファイルの置き場
~/.config/tryton/admin-password   admin のパスワード(本人だけが読める)
```

データは PostgreSQL の中です。本番のサーバーでは、設定を `/etc`、データを `/var/lib` か `/srv` に
置き、専用のユーザーで動かします。

## 手順(2026-10-12 にこの PC で、手順 6 の勘定科目まで動かした)

1. PostgreSQL を apt で入れ、PC のユーザーでデータベースを作れるようにします。会社の人が
   動かします(`ユーザー` は PC のユーザーの名前)

   ```
   sudo apt install postgresql
   sudo -u postgres createuser --createdb ユーザー
   ```

   PC のユーザーで、パスワードなし(OS のユーザーで確かめる peer)でつなげます
2. conda の環境を `~/apps/tryton/.venv` に作り、Tryton を入れます。`sudo` は要りません

   ```
   conda create -p ~/apps/tryton/.venv -c conda-forge python=3.13 pip
   conda activate ~/apps/tryton/.venv
   pip install "trytond[postgresql]==8.0.*" "trytond-sale==8.0.*" "trytond-purchase==8.0.*" "trytond-account-invoice-stock==8.0.*" "trytond-country[data]==8.0.*" "trytond-currency[data]==8.0.*"
   ```

3. 画面の sao を入れます。downloads.tryton.org の `8.0/tryton-sao-8.0.12.tgz` を
   `~/apps/tryton/sao` に展開し、その中で部品を入れます(Node.js の npm を使います)

   ```
   npm install --production --legacy-peer-deps
   ```

4. 設定のファイル `~/apps/tryton/trytond.conf` を書きます。パスワードは書きません

   ```
   [database]
   uri = postgresql://
   path = /home/ユーザー/apps/tryton/files

   [web]
   listen = localhost:8000
   root = /home/ユーザー/apps/tryton/sao
   ```

   Tryton は、決まった場所の設定を読みません。`-c` か `TRYTOND_CONFIG` で渡すので、環境に
   覚えさせます。`localhost` だけで待ち受けるので、同じ LAN からは届きません

   ```
   conda env config vars set -p ~/apps/tryton/.venv TRYTOND_CONFIG=/home/ユーザー/apps/tryton/trytond.conf
   ```

5. データベースを作り、モジュールを入れます。`--all` は、admin のパスワードを聞きます。
   会社の人が端末で打ち込み、忘れないように `~/.config/tryton/admin-password` に書きます
   (フォルダーは 700、ファイルは 600)。メールアドレスは、パスワードを忘れたときにメールで
   送るための物で、空でかまいません(送るには SMTP の設定も要ります)

   ```
   createdb tryton
   trytond-admin -d tryton --all
   trytond-admin -d tryton -u sale purchase account_invoice_stock --activate-dependencies
   trytond_import_countries -c $TRYTOND_CONFIG -d tryton
   trytond_import_currencies -c $TRYTOND_CONFIG -d tryton
   ```

   読み込んだ円は、小数が 2 桁になっています。取引を入れる前に、0 桁、1 円で丸める形に直します
   (`account_jp` のデータで直すまでの間は、データベースの `currency_currency` を直します)
6. 動かし(`trytond`、Ctrl+C で止まります)、`http://localhost:8000` を開いて `admin` で入ります。
   始めのウィザードは、次の順に出ます
   * 利用者: 一人で試すなら、足さずに進みます
   * 会社: 会社も取引先(Party)の 1 つです。名前を作り、通貨 Yen、時間帯 Asia/Tokyo にします
   * 勘定科目: Universal Chart of Accounts から作ります。ふだん使う科目は、売掛金
     Accounts, Notes And Loans Receivable、買掛金 Trade Payables、売上 Goods か Services
     (Revenue の下)、費用 Merchandise, Material, Parts And Supplies です。ブラウザーが
     サインインの名前(admin)を自動で入れることがあるので、消してから選びます。既定は後で
     Financial → Configuration → Configuration で変えられます
7. 日本語にします([aiai_ja](aiai_ja/README.md))。読み込んで trytond を動かし直し、利用者の
   言語を「日本語」にします

   ```
   pip install /リポジトリの場所/tryton/aiai_ja
   trytond_import_ja -c ~/apps/tryton/trytond.conf -d tryton --sao ~/apps/tryton/sao
   ```

8. 1 件通します(まだ確かめていない): 会計年度、お客さん、品目を作り、販売 → 出荷 → 請求書と
   進め、請求書を記帳して、仕訳ができたことを見ます
9. バックアップは PostgreSQL の `pg_dump` と、`files` のフォルダーの写しです

   ```
   pg_dump -Fc tryton > tryton.dump
   ```

## 計画(日本で使うために足す物)

Tryton には日本語の訳がありません(訳がある言葉は 24 で、日本語は入っていません)。日本の
勘定科目と消費税のモジュールもありません(国の物は、フランス、ベルギーなどにあります)。
どちらも、本体に手を入れず、このフォルダーにモジュールとして作ります。

最初の目標は、個人事業の帳簿です。個人が開業するときに、最初に覚えないといけないことだからです。
いま弥生の青色申告や freee 会計を使っている人が、移れるようにします。

1. 動かす: 上の手順で、英語のまま 1 件通します。手順の違いは、ここを直します
2. 個人事業の帳簿(`account_jp`)
   * 個人事業の勘定科目のひな形(事業主貸、事業主借、元入金など)と、円を 0 桁にするデータ
   * 青色申告決算書の形の損益計算書と貸借対照表。確定申告は、その数を国税庁の確定申告書等
     作成コーナーに入れて出します(Tryton から e-Tax には出せません)
   * 弥生と freee の仕訳帳の CSV を読み込む道具
   * 銀行の明細の CSV を読み込み、決まり(`account_statement_rule`)で仕訳にする道具。freee の
     口座連携と自動の仕訳の代わりで、決まりは AI が下書きし、人が確かめます
3. 日本語([aiai_ja](aiai_ja/)、2026-10-12 にできた): 言語 `ja` を作り、14 のモジュールと sao の
   すべての文を訳しました。訳は AI の下書きで、使いながら直します
4. 消費税と請求書(`account_jp` に足す): 10% と軽減の 8%、簡易課税と 2 割特例の計算、適格
   請求書に要る項目(登録番号など)。フランスの `account_fr` の作りを手本にします
5. 減価償却: 日本の定額法と耐用年数に合わせます(`account_asset` を受け継ぎます)
6. 帳票: 見積、請求書を、日本の形の帳票(LibreOffice の `.fodt` のひな形)にします

移るときは、1 年は今の会計ソフトと並べ、決算書の数が合うかを確かめてから切り替えます。
どこまで足すかと、本番に移るかは、使えると分かってから会社や本人が決めます。

## 出典

- Tryton の説明書「How to install Tryton」「Configuration」「Translation」と、8.0 の
  `trytond/commandline.py`(trytond-admin の `-u`、`--activate-dependencies`、`-l`、`TRYTONPASSFILE`)、
  `ir/lang.xml`(言語の一覧)、`sao/README.md`(https://docs.tryton.org/8.0/server/ 、
  https://foss.heptapod.net/tryton/tryton/-/tree/branch/8.0)
- Tryton Release 8.0(https://discuss.tryton.org/t/tryton-release-8-0/9208)、ダウンロードと版の
  決まり(https://www.tryton.org/download)
- trytond(https://pypi.org/project/trytond/)、GPL-3.0-or-later
- Debian の postgresql(https://packages.debian.org/trixie/postgresql)

2026-10-12 に確かめました。
