---
name: aiai-tools-ninshou
description: 会社の認証を PocketBase に集めるのを手伝う。社員は Apple ID か Google ID でサインインし、自分で作るアプリ(API、画面)はみな PocketBase の札(トークン)で人を確かめる。事業用のアプリの会員(お客さん)のサインインも同じ PocketBase で受ける。OSS の道具(Forgejo、Stalwart など)の認証は別に持つ。最初に、社内に認証を管理できる人がいるかを確かめ、管理者の ID と、ドメイン、外部との接続、区画の分離を点検する。
---

# 門番を立てる(認証)

あなたは、この会社が認証を 1 か所に集めるのを手伝います。「誰か」を確かめるのは 1 か所、
「何ができるか」は道具ごとに決めます。専門の言葉は、初めて出るときに 1 度説明してください。

## 守ること

- PocketBase は 1.0 前です。公式の説明書は、v1.0.0 までは前の版との互換を保証せず、changelog を
  読んで手で移行してよいのでなければ、本番の重要なアプリにはまだ勧めない、と書いています。
  FAQ は、ボランティアの個人のプロジェクトで、説明書を読まずに AI の道具だけに頼るなら使わないで、
  とも書いています。版を上げる前に、changelog を会社の人が読みます。このことを最初に開発する人に伝えます
- Apple と Google のクライアント ID とシークレット、PocketBase の管理者(superuser)の
  パスワードは、会社の人が作って入れます。会話にも、リポジトリにも入れません
- 社員の名前とメールアドレスの一覧を、AI への依頼に貼らないでください。人数と、
  どの部署が何を使うかで、設計はできます
- サインインの相手は Apple ID と Google ID にします。Microsoft ID は、Microsoft 365 から
  移る間だけ使う選択肢として伝え、足すかどうかは会社が決めます。1 つ足すたびに、
  登録して手入れする所が 1 つ増えます
- PocketBase は、ほかの道具にサインインを貸す側(OpenID Connect の提供者)にはなりません。
  公式の説明書には、外の OAuth2 でサインインする話だけがあり、提供者になる機能は
  ありません(2026-09-28 に確かめました)。そのため、Forgejo、Stalwart、OnlyOffice、
  Open WebUI の認証は、それぞれの道具が持ちます。1 つにまとめたいときは、
  Forgejo が OpenID Connect の提供者になれます(ただし scope が未実装で、札で何でも
  できることに注意が要ります)。aiseed.dev の自立編には「認証を 1 つに」とありますが、
  aiai tools では、自分で作るアプリの認証を PocketBase に集める、と読み替えています

## 管理できる人がいるか(最初に確かめる)

認証を管理できる人が社内にいなければ、サイバー攻撃は防げません。ほかの手順の前に、これを
確かめます。

1. 管理者の ID を書き出します。ドメインの登録(指定事業者)、DNS、サーバー(SSH の鍵と root)、
   PocketBase の superuser、Forgejo、Stalwart、Apple と Google の開発者のアカウント、回線と
   ルーター、バックアップの置き場、会社が使う外のサービス。何の管理者か、社内の誰が持つか、
   二要素の認証があるか、最後に確かめた日を、会社のリポジトリ([code](../code/))に書きます。
   パスワードと鍵そのものは書きません
2. それぞれを、社内の人が持っているかを確かめます。辞めた人や外の業者だけが持っている物、
   1 人だけが持っている物は、会社の人に伝えます。どうするかは会社が決めます。社内に管理できる
   人がいなければ、それを最初に決めることになります
3. 管理者の ID には、パスキー(W3C の WebAuthn)か、時刻で変わる確認の番号(TOTP、RFC 6238)を
   付けます。JPRS は、安易なパスワードのせいでドメインの登録情報や DNS を書き換えられた事例を
   挙げ、二要素の認証があれば使うよう書いています
4. 人が辞めたり担当を替えたりしたら、その日のうちに、その人の管理者の ID を外します
5. AI がするのは、点検のコマンドと、結果の読み方の下書きです。動かして結果を見るのは、
   管理できる社内の人です。管理者のパスワードと鍵は、AI に渡しません

## 点検する

管理できる人が、決めた間隔で確かめます。

1. 会社のドメイン
   * JPRS の Whois(`https://whois.jprs.jp/`)で、登録者、連絡先、有効期限を見ます。連絡先が
     古いと、変更の知らせが届きません。JP ドメイン名は、廃止しなければ 1 年ごとに自動で
     更新されます。廃止したドメイン名は、一定の期間の後に第三者が登録でき、メールアドレスや
     Web の URL として悪用されえます
   * 指定事業者がレジストリロック(登録情報の変更、移転、廃止を止める仕組み)を扱っていれば、
     使うかを決めます
   * DNS を `dig` で確かめます。NS のサーバーが、そのゾーンを正しく返すか(返さない状態は
     lame delegation で、乗っ取りの元になります)。使うのをやめたサービスを指す CNAME や NS が
     残っていないか(サブドメインの乗っ取りの元になります)。メールの SPF、DKIM、DMARC と、
     証明書を出してよい認証局を決める CAA、DNSSEC の署名

     ```
     dig +short NS example.jp
     dig @NSのサーバー example.jp SOA
     dig +short TXT example.jp
     dig +short TXT _dmarc.example.jp
     dig +short CAA example.jp
     dig +dnssec example.jp SOA
     ```

2. 外部との接続
   * 会社の外の回線(スマートフォンのテザリングや、借りたサーバー)から、会社の外向きの住所を
     RustScan(GPL-3.0)で調べ、開いているのが決めた口(Caddy の 80 と 443、メール、VPN など)
     だけかを確かめます。Nmap はライセンス(NPSL)が OSI の一覧に無いので使いません
   * Certificate Transparency(RFC 9162)のログで、会社のドメインで出された証明書を見ます。
     知らない名前の証明書があれば、使っていないサーバーかサービスが残っています
   * 契約しているプロバイダーから、NICT の NOTICE(推測されやすいパスワードの機器や、古い
     ファームウェアの機器を調べる取り組み)の知らせが来たら、その機器を確かめます
3. 区画の分離
   * 社員、来客、カメラ、錠などの網を分けているなら([network](../network/))、それぞれの網に
     つないだ機械から、ほかの網に、決めた通信だけが通るかを確かめます

## 手順

1. 何に認証が要るかを聞きます。自分で作るアプリ(申し込み、社内の API、文書の蔵、AI の画面)
   と、OSS の道具(Forgejo、メール、会議)を分けて書き出します
2. PocketBase を入れます。実行ファイル 1 つで動きます。公式の説明書は、実行ファイルを
   サーバーに置いて systemd で動かす形です。公式の Docker の画像はありません
   (説明書に「PocketBase doesn't have an official Docker image」とあります)。
   aiseed.dev の例は有志の画像(`ghcr.io/muchobien/pocketbase`)を使っていますが、
   出どころが公式でないので、aiai tools では実行ファイルを置く形にします
   * 実行ファイルを GitHub の Releases から取ります。名前、出どころ、大きさを伝えて
     許しを得てからです
   * `/lib/systemd/system/pocketbase.service` を作ります。公式の例では、
     `ExecStart = /root/pb/pocketbase serve yourdomain.com` とし、`Restart = always` にします。
     ドメインを渡すと、PocketBase 自身が Let's Encrypt の証明書を取ります。
     [server](../server/) の Caddy の後ろに置くなら、`serve --http=127.0.0.1:8090` にし、
     PocketBase の設定で「User IP proxy headers」(`X-Forwarded-For`)を有効にします
   * `systemctl enable pocketbase.service` と `systemctl start pocketbase` で動かします
   * 管理者は、会社の人が `pocketbase superuser create メールアドレス パスワード` で作ります。
     管理の画面は `https://auth.example.jp/_/` です
3. サインインの方法を決めます。`users` のコレクションで、パスワードでのサインインを
   切るか残すか、OAuth2 に Apple と Google を足すかを決めます。PocketBase の OAuth2 には
   Apple と Google と Microsoft が入っています(ソースの `tools/auth/` に `apple.go`、
   `google.go`、`microsoft.go` があります)
   * Google: 会社の人が Google Cloud Console でクライアント ID とシークレットを作り、
     戻り先に `https://auth.example.jp/api/oauth2-redirect` を登録します
   * Apple: 会社の人が Apple Developer Program に登録し、Services ID と鍵(.p8)を作ります。
     会費と、それに含まれる物は、[aiai の CLAUDE.md](https://github.com/aiseed-dev/aiai/blob/main/CLAUDE.md) に書いてあります
4. 自分で作るアプリが人を確かめる方法を決めます。PocketBase の札(JWT)は、コレクションごとの
   秘密の値で署名されます。公開鍵で確かめる形ではないので、アプリは PocketBase に
   `POST /api/collections/users/auth-refresh`(ヘッダーに `Authorization: 札`)を送り、
   返ってきた `record` で人を知ります。aiseed.dev の「蔵」(aiseed-dev/workspace)も、
   この方法(introspection と短い時間のキャッシュ)で確かめています。[api](../api/) に例が
   あります
5. 守りの設定をします。公式の説明書が勧める物です
   * メールは sendmail でなく SMTP(会社のメールサーバー、[mail](../mail/))で送ります
   * Settings の rate limiter を有効にします
   * superuser のサインインを会社の IP アドレスに限ります。MFA も検討します
6. バックアップは `pb_data` を写すだけです。Dashboard > Settings > Backups で、
   S3 互換の置き場にも取れます
7. 古い認証(Entra ID、Google Workspace)と並べて動かし、新しいアプリから順に
   PocketBase に付け替えます。全部を一度に替えません

## 会員(お客さん)のサインイン

事業用のアプリの会員は、社員と別の auth のコレクション(`members`)に置きます。
会員の情報の扱いは [kaiin](../kaiin/) に書いています。

1. サインインの方法を決めます。PocketBase v0.40.4 で使えるのは、パスワード、メールで届く
   一時パスワード(OTP)、OAuth2、MFA(2 つの方法の組み合わせ)です
   * OAuth2 には Apple、Google、Microsoft などが入っています。LINE の専用の提供者はありません
     (汎用の OIDC の枠でつなげるかは確かめていません)
   * パスキー(WebAuthn)はありません。作者は、優先度がとても低いと書いています
   * OTP は既定で無効です。数字なので推測されうるとして、公式は重要なアプリでは MFA と
     組み合わせるよう書いています
2. 守りを入れます。既定で無効な物があります
   * rate limiter を有効にします(新しく入れたときも無効です)
   * `authRule` に `verified = true` を入れると、メールを確かめた人だけがサインインできます
   * 新しい機器からのサインインを知らせるメール(Auth alert)は既定で有効です
   * 札の有効期間は既定で 5 日です。退会や締め出しのときは、その人の `tokenKey` を変えると、
     出した札がすべて使えなくなります
3. メールを日本語にします。確認、パスワードの再設定、OTP のテンプレートはコレクションごとに
   あり、既定は英語です([tsuuchi](../tsuuchi/))
4. 画面は自分で作ります。PocketBase にはサインインの画面が付いていません。OAuth2 の戻り先は
   `https://auth.example.jp/api/oauth2-redirect` です
5. 役割を分けます。会員が自分の役割を書き換えられないよう、API ルールに
   `@request.body.role:isset = false` を足します

## 出典

- PocketBase「Going to production」(https://pocketbase.io/docs/going-to-production/)、
  「Authentication」(https://pocketbase.io/docs/authentication/)、
  「API Records」(https://pocketbase.io/docs/api-records/)。v0.40.4、MIT。
  OAuth2 の提供者の一覧は https://github.com/pocketbase/pocketbase/tree/master/tools/auth
- PocketBase の説明書の最初の注意(https://pocketbase.io/docs/)と FAQ(https://pocketbase.io/faq/)。
  パスキーについての作者の書き込み
  (https://github.com/pocketbase/pocketbase/issues/6800#issuecomment-3341367042)。
  認証の設定の既定の値(https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go)。
  2026-09-29 に確かめました
- JPRS「ドメイン名の乗っ取りに関する注意」(https://jprs.jp/registration/domain-hijacking/)、
  「ドメイン名の廃止に関する注意」(https://jprs.jp/registration/suspended/)、JP ドメイン名の
  ライフサイクル(https://jprs.jp/about/dom-rule/lifecycle/)、レジストリロック
  (https://jprs.jp/about/dom-rule/registry-lock/)、用語辞典の lame delegation
  (https://jprs.jp/glossary/index.php?ID=0176)と Subdomain Takeover
  (https://jprs.jp/glossary/index.php?ID=0267)。2026-10-06 に確かめました
- RFC 6238(TOTP、https://www.rfc-editor.org/rfc/rfc6238)、W3C「Web Authentication Level 3」
  (https://www.w3.org/TR/webauthn-3/)、RFC 7208(SPF)、RFC 6376(DKIM)、RFC 9989(DMARC、
  https://www.rfc-editor.org/rfc/rfc9989)、RFC 8659(CAA)、RFC 9364(DNSSEC)、RFC 9162(CT、
  https://www.rfc-editor.org/rfc/rfc9162)
- BIND 9 の dig(https://bind9.readthedocs.io/en/latest/manpages.html、MPL-2.0)、RustScan
  (https://github.com/bee-san/RustScan、GPL-3.0)、Nmap のライセンス(https://nmap.org/npsl/)
- NICT「NOTICE」(https://notice.go.jp/)
- Forgejo「OAuth2 provider」(https://forgejo.org/docs/latest/user/authentication/oauth2-provider/)。
  「OAuth2 scopes are not yet implemented」とあります
- aiseed-dev/workspace(蔵)の README(https://github.com/aiseed-dev/workspace)
- aiseed.dev「門番を立てる」(https://aiseed.dev/ai-native-ways/software/auth/)。CC BY 4.0

2026-09-28 に確かめました。
