---
name: aiai-tools-network
description: 会社や事務所、民泊の建物のネットワークを、ルーターを買わずに Linux の PC 1 台で組むのを手伝う。フレッツ光と光コラボの接続の方式(PPPoE、IPv6 IPoE、DS-Lite、MAP-E)ごとにできることを分け、systemd-networkd、nftables、dnsmasq、Unbound、WireGuard、hostapd で、NAT、ファイアウォール、DHCP、DNS、VLAN、VPN、Wi-Fi を作る。
---

# ネットワークを組む(Linux の PC をルーターにする)

あなたは、この会社が、Linux の PC をルーターにしてネットワークを組むのを手伝います。
設定は AI が下書きし、コマンドは会社の人が動かします。専門の言葉は、初めて出るときに
1 度説明してください。

## 守ること

- 回線の ID とパスワード(PPPoE の認証)、WireGuard の秘密鍵、Wi-Fi のパスフレーズは、
  会社の人が入れます。会話にも、リポジトリにも入れません
- 設定を替えるときは、今の設定を写してから替え、戻す手順を先に書きます。リモートから替えると
  自分が締め出されることがあるので、初めは PC の前で替えます
- Wi-Fi のカードや USB の子機は、技適マークのある物だけを使います。マークの無い無線機を
  使うと電波法違反になる場合があります。特例の届出の制度は、実験のための 180 日の物で、
  会社のふだんの Wi-Fi には使えません
- ダウンロードとインストール(apt)は、名前、出どころ、大きさを伝えて許しを得てからにします

## 回線の方式ごとにできること(2026-09-29 に確かめた)

| 方式 | Linux でできるか | 要ること |
|---|---|---|
| PPPoE(IPv4) | できる | pppd の `plugin pppoe.so`(systemd-networkd は PPPoE を扱えない)。MTU は 1454 |
| IPv6 IPoE | できる | systemd-networkd で DHCPv6-PD を受け(`DHCPPrefixDelegation=`)、LAN に RA で配る(`IPv6SendRA=`)。MTU は 1500 |
| DS-Lite(transix、クロスパス、v6 コネクト) | できる | systemd-networkd の `Kind=ip6tnl`、`Mode=ipip6`。相手(AFTR)は transix が `gw.transix.jp`、クロスパスが `dgw.xpass.jp`。VNE が自作の Linux を対応ルーターとして認めるかは確かめていない |
| MAP-E(v6プラス、OCN バーチャルコネクト) | 正規の道が無い | v6プラスのルールは、NDA を結んだ機器の作り手にだけ開示される(JPIX の開発ガイド)。IPv4 は、対応のホームゲートウェイか対応ルーターに任せ、Linux はその後ろに置く |

- 光ネクストの IPv6 IPoE では、網が RA を送り、M フラグが 1 なら DHCPv6-PD で /48 か /56 を
  受けます。そうでなければ RA の /64 だけです(NTT 東日本の技術参考資料)。ひかり電話の契約の
  有無でこれが変わる、と書いているのはメーカーの資料です
- ひかり電話を使うなら、NTT のひかり電話対応機器(ホームゲートウェイ)を残します。汎用の
  Linux は対応機器になりません。Linux はその後ろに置き、ホームゲートウェイから DHCPv6-PD を
  受けます

## 使う物

| 役目 | 物 | ライセンス |
|---|---|---|
| つなぎ方、IPv6、VLAN、トンネル | systemd-networkd(systemd v262、Ubuntu 26.04 は 259.5) | LGPL-2.1 |
| ファイアウォールと NAT | nftables 1.1.7 | GPL |
| DHCP | dnsmasq 2.93 | GPL |
| DNS | Unbound 1.26.1 | BSD-3-Clause |
| VPN | WireGuard(カーネルに入っている)と wireguard-tools | GPL-2.0 |
| Wi-Fi の親機 | hostapd 2.12 | BSD |
| PPPoE | pppd(ppp 2.5) | ファイルごとに BSD 系、GPL、MIT |


## 手順

1. 今の回線を聞きます。回線(光ネクスト、光クロス)、プロバイダーと IPv4 の方式(PPPoE、
   DS-Lite、MAP-E)、ひかり電話の有無、ホームゲートウェイがあるか、部屋と機器の数、
   Wi-Fi が要るか、外から入る必要(VPN)があるか
2. 置き方を決めます。上の表のとおり、MAP-E かひかり電話なら、ホームゲートウェイの後ろに
   置きます。それ以外なら、ONU の直後に置けます。会社が決めます
3. PC を用意します。LAN の口は 2 つ以上です(1 つなら、管理型のスイッチと VLAN で分けます)。
   Ubuntu の LTS を入れます([server](../server/))
4. 設定を下書きします。すべてテキストのファイルで、会社のリポジトリ([code](../code/))に置きます
   * `/etc/systemd/network/`: WAN と LAN の `.network`、トンネルと VLAN の `.netdev`。
     LAN の側に `IPMasquerade=ipv4` と `IPv6SendRA=yes`、WAN の側に DHCPv6-PD
   * `/etc/nftables.conf`: input と forward を既定で落とし(`policy drop`)、行きの続き
     (`ct state established,related`)と、IPv6 の近隣探索の ICMPv6 だけを通します。IPv6 には
     NAT が無いので、forward の既定を落とすことが守りになります。UPnP は入れません
   * DHCP と DNS: dnsmasq で LAN に配り、Unbound で名前を引きます
   * VLAN: 分けた網どうしは、要る通信だけを nftables で通します
   * VPN: 外から入る人ごとに WireGuard の鍵を作ります
   * Wi-Fi: 技適マークのあるカードで、hostapd を `country_code=JP` で動かします
5. 並べて確かめます。今のルーターを残したまま、PC を別の口で試し、つながること、IPv6 が
   配られること、外から入れないことを確かめてから、切り替えます
6. 更新を自動にします。Ubuntu Server は unattended-upgrades で、セキュリティの更新を毎日
   当てます。有効かを確かめます
7. 記録を残します。回線の方式、配っている範囲、VLAN の分け方、開けた口を、リポジトリの
   README に書きます。次に替えるとき、AI がそれを読んで作り直せます
8. 会社のネットワークなら、PC の記録を別の機械に送ります。サインイン、設定の変更、更新、VPN の接続、
   止めた通信の 5 つを出し、記録の機械へ送ります。出し方と送り方は [router](../router/) の
   「記録を全部残せるのは Linux の箱」と「記録を別の機械に置く」にあります。毎朝の点検は [tenken](../tenken/) です

## 出典

- NTT 東日本「IP 通信網サービスのインタフェース 第三分冊」第 46 版(https://flets.com/pdf/ip-int-3.pdf)
- ヤマハ「IPv6 IPoE」(https://www.rtpro.yamaha.co.jp/RT/docs/ipoe/index.html)、「DS-Lite」
  (https://network.yamaha.com/setting/router_firewall/ipv6/ds-lite)
- インターネットマルチフィード transix DS-Lite(https://www.mfeed.ad.jp/transix/dslite/)。
  TP-Link の AFTR の例(https://www.tp-link.com/jp/support/faq/2262/)。朝日ネット v6 コネクト
  (https://asahi-net.jp/biz/service/option/ipv6/4over6.html)
- JPIX「v6プラス」(https://www.jpix.ad.jp/service/?p=3444)、開発ガイド
  (https://www.jpix.ad.jp/files/developer_guide_v6plus_v1.3.pdf)
- フレッツ光「ひかり電話対応機器」(https://flets.com/denwa/hikaridenwa/subscription/router.html)
- systemd の `systemd.network` と `systemd.netdev`(https://github.com/systemd/systemd/blob/main/man/systemd.network.xml、
  https://github.com/systemd/systemd/blob/main/man/systemd.netdev.xml)。pppd の PPPoE
  (https://github.com/ppp-project/ppp/blob/master/README.pppoe)
- nftables(https://www.netfilter.org/projects/nftables/index.html)と wiki の家庭のルーターの例
  (https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_home_router)。RFC 6092
  (https://www.rfc-editor.org/rfc/rfc6092.html)
- dnsmasq(https://thekelleys.org.uk/dnsmasq/doc.html)、Unbound(https://github.com/NLnetLabs/unbound)、
  WireGuard(https://www.wireguard.com/install/)、hostapd(https://w1.fi/hostapd/)
- 総務省 電波利用ホームページ: 技適マーク(https://www.tele.soumu.go.jp/j/adm/monitoring/summary/qa/giteki_mark/index.htm)、
  特例制度(https://www.tele.soumu.go.jp/j/sys/others/exp-sp/index.htm)
- Ubuntu「Automatic updates」(https://ubuntu.com/server/docs/how-to/software/automatic-updates/)

2026-10-06 に見直しました(版と資料は 2026-09-29 に確かめた)。
