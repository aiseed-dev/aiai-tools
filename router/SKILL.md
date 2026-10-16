---
name: aiai-tools-router
description: 会社のネットワークのルーターを選び、組み、記録を別の機械に置くのを手伝う。答えを先に出さず、拠点、区画、外から入る人、今の機器と保守の契約、止めてよい時間を尋ね、選ぶと何が変わるかを伝える。選ぶ条件の第一は、記録を別の機械へ送れるか(syslog)。区画ごとに止められる形に組み、ルーターと VPN の記録を別の区画の記録の機械に送り、毎日点検する(tenken)
---

# 会社のルーターを選び、記録を残す

あなたは、この会社がネットワークのルーターを選び、組み、その記録を残すのを手伝います。設定は
AI が下書きし、コマンドは会社の人が動かします。決めるのは会社の人です。専門の言葉は、初めて
出るときに 1 度説明してください。

## 守ること

- 答えを先に出しません。下の「尋ねること」を聞き、選ぶと何が変わるかを伝え、決めるのは会社の人です
- 管理画面のパスワード、VPN と TLS の秘密鍵、回線の ID とパスワードは、会社の人が入れます。会話にも、
  リポジトリにも入れません
- 機器の設定を替える前に、今の設定を写し、戻す手順を先に書きます。初めは機器の前で替えます
- AI は機器につなぎません。機器の記録も、記録の機械にある写しを読みます
- 機器の機能は、その機種と版の説明書で確かめます。下の例は確かめた範囲だけで、ほかの機種に
  当てはめません

## 尋ねること

| 尋ねること | 答えで変わること |
|---|---|
| 拠点の数と、拠点の間のつなぎ方 | 拠点ごとに境界の機器を置くか。拠点の間の VPN の数 |
| 区画(社員、来客、機器、管理)と、それぞれの台数 | 区画の数と、区画の間で通してよい通信 |
| 外から入る人(在宅、出先、保守の会社)と、その数 | 外に開く VPN の口と、人ごとの鍵の数 |
| 今の機器と、保守の契約(期限、誰が更新するか) | 今の機器を使い続けるか。入れ替えの時期 |
| 止めてよい時間(曜日、時間帯、何分まで) | 入れ替えと設定の替え方、予備の機器が要るか |
| 記録を誰が読み、どれだけ残すか | 記録の機械の大きさと置き場所 |

## 選ぶ条件の第一: 記録を別の機械へ送れるか

ルーターに残った記録は、電源を切ると消える物や、管理画面で見るだけの物があります。破られたときに
いちばん要るのは、何が起きたかの記録です。そのため、記録を起きたその時に別の機械へ送れるか
(syslog。RFC 5424 が書式、RFC 5426 が UDP の 514 番、RFC 5425 が TLS の 6514 番)を、最初に
確かめます。確かめ方は、その機種の説明書で「syslog」「ログの送信先」を探すことです。

確かめた例(2026-10-16):

- ヤマハ RTX: `syslog host` で送り先を 4 か所まで。`syslog execute command on` で実行したコマンドを残す
  (初めは off)。`syslog notice on` でフィルターが見つけたパケットを残す(初めは off)。
  `syslog format type rfc5424` で RFC 5424 の書式にできる(版の条件がある)。管理画面への
  サインインとファームウェアの入れ替えがどのメッセージで出るかは、説明書の中で確かめていません
- NEC UNIVERGE IX: 出力先に syslog サーバーがあり、送り先は ver.7.2 以降で 8 か所まで。レベルは 5 段階
- アライドテレシス AT-AR シリーズ: `log host` で送り先を決め、出す物をフィルターで決める
- Cisco IOS XE: `logging host` で送り先を決め、TCP でも送れる
- OpenWrt: `/etc/config/system` の `log_ip`、`log_port`、`log_proto`(tcp か udp)
- 家庭向けの例(NEC Aterm WG1810HP(JE)): 説明書のログのページは、管理画面で見てファイルに保存する
  形で、電源を切ると消えます。外へ送る設定は、そのページには書かれていません

## 3 つの選び方

| 選び方 | 何が変わるか |
|---|---|
| 記録を送れる業務用のルーター | メーカーの更新と保守の契約に頼れる。記録の中身は機種で決まる |
| OpenWrt を入れたルーター | 更新は自分で入れる。記録は syslog で送れる。入れられる機種は限られる |
| Linux の箱を境界のルーターにする([network](../network/)) | 記録と設定を全部自分で持つ。更新も守りも自分でする。市販の機器は無線と転送だけにする |

今の機器が記録を送れないときは、すぐに入れ替えず、通り道に Linux の箱をブリッジ(通信を素通しする
つなぎ方)として置き、通る通信を数えて記録を送ります。この手順は [network](../network/) にまだ無いので、
その時点の systemd-networkd と nftables の説明書で下書きします。次の入れ替えで、記録を送れる物にします。

## 組み方

- 区画を境界の機器 1 台に集めず、区画ごとに止められる形にします。どこかが破られたとき、その区画だけを
  止めて、ほかの仕事を続けられるようにするためです
- 機器の管理画面へ行く通信は、管理の区画からだけ通します
- 外に開く VPN は WireGuard にします(UDP の上で動き、カーネルの部品は GPLv2)。人ごとに鍵を分け、
  辞めた人の鍵はその日に消します

## 記録を別の機械に置く

1. 記録の機械を、ほかとは別の区画に置きます。機器からは、記録の口(514 か 6514)へ送ることしか
   できないようにし、記録の機械の管理の口へは、管理の区画からだけ入れるようにします
2. 受ける側は rsyslog(GPLv3)です。機器ごとに 1 つのファイルに分けて置きます(`dynaFile` の
   テンプレート。名前に機器の名前を使うときは、説明書のとおり安全な形にします)。機器が TLS で
   送れるなら TLS で受け、相手を絞ります(rsyslog の見本は相手を絞らない `anon` なので、そのまま
   写しません)。systemd-journal-remote は journal の形を受ける物で、ルーターの syslog は受けません
3. 残す物は、管理画面へのサインイン、設定の変更、ファームウェアの入れ替え、VPN の接続、止めた通信です。
   その機種で出せる物を説明書で確かめ、出せない物は出せないと書いておきます
4. すべての機器の時刻を、同じ時計に合わせます(NTP、RFC 5905)。時刻がずれると、記録を突き合わせられません

## 順番

1. 今の機器が記録を送れるかを、説明書で確かめます
2. 記録の機械を作り、機器から送ります。届いたかを、記録の機械で確かめます
3. 毎日の点検([tenken](../tenken/))を動かします

## 出典

- RFC 5424(https://www.rfc-editor.org/rfc/rfc5424)、RFC 5425(https://www.rfc-editor.org/rfc/rfc5425)、
  RFC 9662(https://www.rfc-editor.org/rfc/rfc9662)、RFC 5426(https://www.rfc-editor.org/rfc/rfc5426)、
  RFC 5905(https://www.rfc-editor.org/rfc/rfc5905)
- ヤマハ「コマンドリファレンス」syslog host、syslog execute command、syslog notice、syslog format type、ntpdate
  (https://www.rtpro.yamaha.co.jp/RT/manual/rt-common/toc.html)
- NEC UNIVERGE IX「FAQ」ログ(https://jpn.nec.com/univerge/ix/faq/els.html)
- アライドテレシス AT-AR3050S/AR4050S「コマンドリファレンス」log host
  (https://www.allied-telesis.co.jp/support/list/awp/rel/5.5.4-1.2/613-002107_BD/docs/)
- Cisco「Network Services Configuration Guide, Cisco IOS XE 17.x」
  (https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ntw-servs/b-network-services/m_ip6-emb-mgmt.html)
- OpenWrt「System configuration」(https://openwrt.org/docs/guide-user/base-system/system_configuration)
- NEC Aterm WG1810HP(JE)「通信情報ログ」(https://www.aterm.jp/function/wg1810hp_je/guide/log.html)
- rsyslog「imtcp」「Templates」「Licensing」(https://docs.rsyslog.com/doc/configuration/modules/imtcp.html 、
  https://docs.rsyslog.com/doc/configuration/templates.html 、https://docs.rsyslog.com/doc/licensing.html)
- systemd「systemd-journal-remote.service」
  (https://github.com/systemd/systemd/blob/main/man/systemd-journal-remote.service.xml)
- WireGuard(https://www.wireguard.com/)

2026-10-16 に確かめました。
