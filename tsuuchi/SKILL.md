---
name: aiai-tools-tsuuchi
description: 事業用のアプリから会員に、取引の通知(招待、予約の確認、案内)をメールと Web Push、スマホのアプリの通知(APNs、FCM)で届けるのを手伝う。広告は入れない。Gmail と Yahoo の送信者の決まりに合わせる。
---

# 知らせを届ける(通知)

あなたは、この会社のアプリが会員に知らせを届ける仕組みを作るのを手伝います。
専門の言葉は、初めて出るときに 1 度説明してください。

## 守ること

- SMTP のパスワード、VAPID の秘密鍵、APNs の鍵(`.p8`)、FCM のサービスアカウントの JSON は、
  開発する人が作って `.env` か、リポジトリの外のファイルに置きます。会話にも、リポジトリにも入れません
- 会員のメールアドレスの一覧と、送った中身を、AI への依頼に貼りません。テンプレートは、
  差し込む欄の名前(`{予約の日}`)で作ります
- 通知には広告を入れません。広告や宣伝を含まず、広告のサイトへも誘わない取引の通知は、
  特定電子メール法の「特定電子メール」に当たりません(総務省と消費者庁のガイドライン)。
  広告を添えると当たり、前もっての同意や表示の決まりがかかります
- 通知そのものには、メッセージの本文、名前、予約の中身など、会員の情報を入れません。
  「新しいメッセージがあります」とだけ送り、中身はアプリがサインインして取りに行きます。通知は
  Apple、Google、中継の会社を通り、ロック画面にも出ます(Apple も、通知に顧客の情報を入れないよう
  書いています)

## 調べること

Gmail と Yahoo が求める送信者の決まり(SPF、DKIM、DMARC、逆引き、迷惑メールの報告率)と、Web Push
の決まり(iPhone と iPad はホーム画面に追加した Web アプリだけ、許可を求めるのは利用者がボタンを
押したときだけ)を、その時点の各社の説明で調べ、送る道の設定に入れます。

スマホのアプリの通知では、端末の宛先(プッシュトークン)と端末の情報が、Apple、Google、中継の会社に
送られます。個人情報保護法の委託や第三者への提供、電気通信事業法の外部送信規律に当たるかを、その時点の
資料で調べ、プライバシーポリシーと、アプリの中の知らせに入れます。

## 手順

1. 何を知らせるかを書き出します(招待、同意の文が変わったこと、予約の確認、前日の案内、
   新しいメッセージ)
2. 送る道を決めます。自分のメールサーバー([mail](../mail/) の Stalwart)から送るか、中継の
   サービス(SMTP リレー)を使うかです。中継を使うと、会員のアドレスを中継の会社に預けるので、
   [kaiin](../kaiin/) の委託として扱います
3. メールを送ります。アプリのサーバーから SMTP で送ります。PocketBase なら、Settings > Mail
   settings で SMTP を設定し(既定の sendmail は使いません)、フック(`pb_hooks` の `*.pb.js`)で
   `$app.newMailClient().send(...)`、決まった時刻の知らせは `cronAdd` で送ります
4. Web Push を送ります。画面(Web アプリ)で購読してもらい、購読の情報を会員に付けて置き、
   サーバーから pywebpush(MPL-2.0、2.5.0)で送ります。VAPID の鍵は会社の人が作ります
5. スマホのアプリの通知を送ります。iPhone は APNs、Android は FCM を通ります。送り方は 2 つで、
   どちらにするかは、作る人が決めます
   * 自分のサーバーから直接送る: APNs は `.p8` の鍵で作ったトークン(20〜60 分ごとに作り直す)で
     HTTP/2 で送り、FCM は HTTP v1 API にサービスアカウントの札で送ります。宛先が渡るのは Apple と
     Google だけです
   * 中継のサービス(OneSignal など)を使う: 両方を 1 つの口で送れて、送った数などを画面で見られます。
     宛先と送る中身が中継の会社にも渡るので、委託先が 1 つ増えます([kaiin](../kaiin/))
   宛先は会員に付けて置き、サインアウトや退会のときに消します
6. 届いたかを見ます。迷惑メールの報告率を見て、送った記録を残します

## 出典

- Google「Email sender guidelines」(https://support.google.com/mail/answer/81126)。Yahoo
  「Sender Best Practices」(https://senders.yahooinc.com/best-practices/)
- 総務省・消費者庁「特定電子メールの送信等に関するガイドライン」
  (https://www.soumu.go.jp/main_sosiki/joho_tsusin/d_syohi/pdf/m_mail_081114_1.pdf)
- PocketBase「Sending emails」(https://pocketbase.io/docs/js-sending-emails/)、
  「Job scheduling」(https://pocketbase.io/docs/js-jobs-scheduling/)。v0.40.4
- Stalwart(https://github.com/stalwartlabs/stalwart)v0.16.24
- RFC 8030(https://www.rfc-editor.org/info/rfc8030)、RFC 8291(https://www.rfc-editor.org/info/rfc8291)、
  RFC 8292(https://www.rfc-editor.org/info/rfc8292)。WebKit「Web Push for Web Apps on iOS and iPadOS」
  (https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)。pywebpush
  (https://pypi.org/pypi/pywebpush/json)
- Apple「Generating a remote notification」
  (https://developer.apple.com/documentation/usernotifications/generating-a-remote-notification)、
  「Establishing a token-based connection to APNs」
  (https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns)
- Firebase「Send messages using the HTTP v1 API」(https://firebase.google.com/docs/cloud-messaging/send/v1-api)

2026-10-12 に確かめました。
