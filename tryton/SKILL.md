---
name: aiai-tools-tryton
description: ERP とは何かを伝え、Tryton(GPL-3.0 の OSS の ERP)の 8.0 LTS を、自分の PC(Debian)で PostgreSQL と conda の環境で、Docker を使わずに動かすのを手伝う。日本で使うために足す物(日本語の訳、日本の勘定科目と消費税)を、本体に手を入れずに、ファイルに書いたモジュールとして作る。
---

# Tryton を自分の PC で動かす

あなたは、この会社の人が ERP とは何かを知り、Tryton を自分の PC で動かして触れるように
するのを手伝います。専門の言葉は、初めて出るときに 1 度説明してください。

## 守ること

- 秘密の値(パスワード)を、会話にも、リポジトリにも書きません。管理者のパスワードは、会社の人が
  ファイルに入れ、`TRYTONPASSFILE` で渡します
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

## 組み合わせ(2026-10-12 に配布元で確かめた。まだ動かしていない)

| 物 | 版 | ライセンス |
|---|---|---|
| Tryton(trytond と各モジュール) | 8.0 LTS(8.0.11、2026-10-01) | GPL-3.0-or-later |
| sao(Web の画面) | 8.0.12 | GPL-3.0-or-later |
| PostgreSQL(Debian 13 の物) | 17 | PostgreSQL License |
| Python、Node.js(conda-forge) | 3.13、24 | PSF、MIT |

8.0 は長期の支援版で、支援は 5 年です。ふつうの版は 6 か月ごとに出て、支援は 1 年です。
Tryton が使えるデータベースは PostgreSQL と SQLite だけで、MariaDB は使えません。

## 手順

1. PostgreSQL を入れ、PC のユーザーでデータベースを作れるようにします。会社の人が動かします
   (`ユーザー` は PC のユーザーの名前)

   ```
   sudo apt install postgresql
   sudo -u postgres createuser --createdb ユーザー
   ```

   PC のユーザーで、パスワードなし(OS のユーザーで確かめる peer)でつなげます
2. 部品を conda の環境に入れます。`sudo` は要りません

   ```
   conda create -n tryton -c conda-forge python=3.13 nodejs=24 pip
   conda run -n tryton pip install "trytond[postgresql]==8.0.*" "trytond-sale==8.0.*" "trytond-purchase==8.0.*" "trytond-account-invoice-stock==8.0.*" "trytond-country[data]==8.0.*" "trytond-currency[data]==8.0.*"
   ```

   sao は、downloads.tryton.org の `8.0/tryton-sao-8.0.12.tgz` を展開し、その中で部品を入れます

   ```
   npm install --production --legacy-peer-deps
   ```

3. 設定のファイル `trytond.conf` を書きます。パスワードは書きません

   ```
   [database]
   uri = postgresql://
   path = /home/ユーザー/tryton/files

   [web]
   listen = localhost:8000
   root = /home/ユーザー/tryton/sao
   ```

   `localhost` だけで待ち受けるので、同じ LAN からは届きません
4. データベースを作り、モジュールを入れます。管理者のパスワードは、会社の人が作ったファイルから
   読ませます

   ```
   createdb tryton
   export TRYTOND_CONFIG=/home/ユーザー/tryton/trytond.conf
   TRYTONPASSFILE=パスワードのファイル trytond-admin -d tryton --all --email 管理者のメールアドレス
   trytond-admin -d tryton -u sale purchase account_invoice_stock --activate-dependencies
   trytond_import_countries -c $TRYTOND_CONFIG -d tryton
   trytond_import_currencies -c $TRYTOND_CONFIG -d tryton
   ```

5. 動かします。止めるまで動き続けます(Ctrl+C で止まります)

   ```
   trytond
   ```

6. `http://localhost:8000` を開き、`admin` で入ります。始めのウィザードで会社(通貨は JPY)と
   勘定科目を作り、お客さん、品目を 1 つずつ作って、販売 → 出荷 → 請求書と進め、請求書を
   記帳して、仕訳ができたことを見ます
7. バックアップは PostgreSQL の `pg_dump` と、`path` のフォルダーの写しです

   ```
   pg_dump -Fc tryton > tryton.dump
   ```

## 計画(日本で使うために足す物)

Tryton には日本語の訳がありません(訳がある言葉は 24 で、日本語は入っていません)。日本の
勘定科目と消費税のモジュールもありません(国の物は、フランス、ベルギーなどにあります)。
どちらも、本体に手を入れず、このフォルダーにモジュールとして作ります。

1. 動かす: 上の手順で、英語のまま 1 件通します。手順の違いは、ここを直します
2. 日本語(`aiai_ja`): 言語 `ja` を足し(本体の言語の一覧にないので、データとして書きます)、
   モジュールごとの訳を `locale/` の PO ファイルに書きます。言葉は、ERPNext で作った用語集
   ([erpnext/aiai_ja/yougo.csv](../erpnext/aiai_ja/yougo.csv))にそろえます。訳の無い文と、
   差し込み(`%s` など)の数が合うかを確かめる道具も作ります
3. 日本の会計(`account_jp`): 勘定科目のひな形、消費税(10% と軽減の 8%)、適格請求書に
   要る項目(登録番号など)を書きます。フランスの `account_fr` の作りを手本にします
4. 帳票: 見積、請求書を、日本の形の帳票(LibreOffice の `.fodt` のひな形)にします

どこまで足すかと、本番に移るかは、使えると分かってから会社が決めます。

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
