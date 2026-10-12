---
name: aiai-tools-kaiseki
description: 自分のサイトのアクセス解析を、Google Analytics と AdSense に頼らず、自分のサーバーで持つのを手伝う。Google Analytics と同じ程度の記録を自分のサーバー(analytics.aiseed.dev など)に集め、受け入れた人は Cookie の ID と会員で積み上げ、集計と決まりと機械学習でその人の関心を出し、自社のサービスの案内と、売った協賛の広告に使う。
---

# 自分で集めて、自分のサービスに使う(解析)

あなたは、この会社が、サイトの解析と広告を自分の側で持つのを手伝います。データを Google だけに
集めず、自分のサーバーに積み上げ、会社の事業の元手にします。使い道は、まず自社のサービス(案内と
改善)で、その上に、協賛の広告の枠を売る事業を乗せます。専門の言葉は、初めて出るときに 1 度
説明してください。

## 守ること

- Cookie を受け入れるかは、本人が選びます。受け入れない人には ID を置かず、数だけを数えます
- 本人が、自分の ID の記録と、会員とのひもづけを見て、消せるようにします
- 会員とのひもづけは、会員のサーバーだけが持つトークンで受け付けます。ブラウザーからはさせません
- 記録は自分のサーバーの中で処理し、外のサービスに渡しません
- 協賛の広告主に渡すのは、表示と押された数と、その先の結果の合計だけです。見た人の記録は渡しません。
  協賛の枠には「広告」と書きます
- IP アドレスは記録しません(Google Analytics 4 と同じ)。受け口の前の Caddy にもアクセスの
  記録(`log`)を付けません
- 合言葉(`KAISEKI_TOKEN`、`KAISEKI_LINK_TOKEN`)は、会社の人が作って入れます。会話にも、
  リポジトリにも入れません

## 調べること

ブラウザーに利用者の情報を送らせるので、電気通信事業法の外部送信規律と、個人情報保護法を、その時点の
資料で調べ、知らせのページ(`/kaiseki/`)と、会員の同意の文([kaiin](../kaiin/))に入れます。送り先が
自分のサーバーでも調べます。協賛の広告を載せるなら、広告の表示の決まりも調べます。

## 作り

| ファイル | 役目 |
|---|---|
| [kaiseki.js](kaiseki.js) | ページに置くスクリプト。受け入れるかを聞き、表示、見ていた時間、出来事を送る。自分のサイトどうしのリンクで ID を引き継ぐ |
| [server.py](server.py) | analytics.aiseed.dev の受け口。標準ライブラリと SQLite。記録、本人が見る・消す、会員とのひもづけ、集計 |
| [test_server.py](test_server.py) | 受け口の確かめ |
| [d1/](d1/) | 先に作った、Cloudflare Pages の Functions と D1 で数えて広告を差し込む見本 |

集める項目は、Google Analytics とほぼ同じです。サイト、ページ、題、参照元のホスト、キャンペーン
(`utm_`)、言語、時間帯、画面の大きさ、ブラウザー、ページを見ていた時間と、どこまで下へ見たか(%)、出来事と、その短い値。受け入れた人の
分には、Cookie の ID と、訪問(タブ)の ID が付きます。受け入れない人には、どちらの ID も置かず、
数だけを数えます。

- 受け入れるかの帯は、画面の下に固定して出します。暗い表示では暗い色になります。帯の見た目は
  優先の度合いを持たない(`:where()`)ので、サイトの `#kaiseki-bar` の CSS がそのまま勝ちます
- 受け入れたときに、出来事 `accept` を ID 付きで送るので、そのページから数えられます
- 自分のサイトどうしのリンクを渡るときは、ID を URL の `#` の後ろ(`#kaiseki_id=`)に載せて
  引き継ぎ、行き先で受け入れたことにします。`#` の後ろはサーバーに送られないので、配信の記録に
  残りません
- ページを見ていた時間(出来事 `leave`)は、タブを切り替えるたびに送るので、集計では合計します

受け口の口は次のとおりです。

| 口 | 誰が | すること |
|---|---|---|
| `POST /v1/hit` | ページ | 記録を 1 つ足す |
| `GET /v1/mine?vid=`、`POST /v1/forget` | 本人 | 自分の記録を見る、消す |
| `POST /v1/link`、`POST /v1/forget-member` | 会員のサーバー(`KAISEKI_LINK_TOKEN`) | ID を会員にひもづける、退会した会員を消す |
| `GET /v1/report`、`GET /v1/member` | 会社の人(`KAISEKI_TOKEN`) | ページごとの集計、会員ごとの記録 |

## 手順

1. 受け口を置きます。外から HTTPS で届く機械で `server.py` を動かし、Caddy から
   `analytics.aiseed.dev` で出します([server](../server/))。`KAISEKI_SITES` を空にすると、
   HTTPS のどのサイトからでも受けます(記録のサイトが、ブラウザーの送り元と同じときだけ)。書くと、
   そのサイトに限ります。報告はサイトごとに分かれます。手元で試すときだけ、`KAISEKI_ORIGINS` に `http://127.0.0.1:8001` のような
   送り元を足すと、ページから自分の記録を読めます
2. 各ページに置きます。`data-own` には、ID を引き継ぐ自分のサイトのドメインを書きます

   ```
   <script src="/kaiseki.js" data-to="https://analytics.aiseed.dev" data-own="time-j.net aiseed.dev" defer></script>
   ```

   ID を使わないサイトは `data-ask="no"` を付けます。帯を出さず、Cookie の ID も訪問の ID も置かず、
   表示、見ていた時間、出来事を数だけ送ります。帯の問いの文は `data-ask-text` で替えられます

3. 知らせのページ(`/kaiseki/`)を書きます。送る情報(上の項目と、Cookie の ID と訪問の ID)、
   送り先、目的、自分のサイトどうしで ID を引き継ぐこと、Cookie を受け入れるかを変える方法
   (`kaiseki.choose(true)` と `kaiseki.choose(false)`)、自分の記録を見て消す方法(`/v1/mine` と
   `kaiseki.forget()`)
4. 会員のサーバーが、サインインのときに、ページから `kaiseki.id()` を受け取り、`/v1/link` に送ります。
   退会のときは `/v1/forget-member` に送ります
5. 申し込みなど、結果にあたる所で `kaiseki.event("signup")` のように出来事を送ります。検索の言葉の
   ように値を付けるときは `kaiseki.event("search", {value: "雨"})` とします(100 文字まで)。値には
   入力された文が入るので、知らせのページに書きます
6. 関心を出して、案内と広告を選びます。汎用の AI は要りません
   * 関心: 会員や ID ごとに、よく見る地点、季節、分野を SQL で数えます
   * 選び方: 「この地域の地点を見る人には、この協賛」のような決まりで選びます
   * 予測(押されやすさなど)が要るなら、[bunseki](../bunseki/) の機械学習を使います
   * 何をどう使うかは会社が決めます
7. 協賛を売るなら、値段、載せない広告の決まり、請求(適格請求書)を会社が決めます。広告主への報告は、
   合計だけにします
8. 確かめます

   ```
   python kaiseki/test_server.py
   ```

## 出典

- Google「Trademark list」(https://about.google/brand-resource-center/trademark-list/)。商標は
  「Google Analytics」で、「Analytics」だけではありません
- 総務省「外部送信規律 FAQ」(https://www.soumu.go.jp/main_sosiki/joho_tsusin/d_syohi/gaibusoushin_kiritsu_00002.html)
- 消費者庁「ステルスマーケティング」
  (https://www.caa.go.jp/policies/policy/representation/fair_labeling/stealth_marketing/)
- Cloudflare「Middleware」(https://developers.cloudflare.com/pages/functions/middleware/)、
  「Pricing」(https://developers.cloudflare.com/pages/functions/pricing/)、D1「Pricing」
  (https://developers.cloudflare.com/d1/platform/pricing/)。先に作った見本の分
- Google「IP masking in Google Analytics」(https://support.google.com/analytics/answer/2763052)。
  GA4 は IP アドレスを記録も保存もしない、とあります
- Node.js「SQLite」(https://nodejs.org/docs/latest-v24.x/api/sqlite.html)

2026-10-07 に確かめました。
