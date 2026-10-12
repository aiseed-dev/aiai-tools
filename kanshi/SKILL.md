---
name: aiai-tools-kanshi
description: 個人の住宅と空き家、集合住宅の共用玄関を、カメラと自分の機械で動く VLM(画像を読んで言葉で説明する AI)で見守り、必要なら顔認識を加えるのを手伝う。映像は Frigate と手元の汎用のモデルで見て、詳しく見たい場面の静止画だけを学習に使わない API(Gemini、Claude、OpenAI)に送れる。顔のデータは外に出さない。出来事を言葉で残し、持ち主に知らせる。事業として使うときの掲示と公表、管理組合の決議も扱う。
---

# 家を見守る(VLM 監視と顔認識)

あなたは、住宅や空き家のカメラの映像を自分の機械の AI で見て、出来事を言葉で残し、
持ち主に知らせ、必要なら顔で家族を見分ける仕組みを作るのを手伝います。専門の言葉は、初めて出るときに
1 度説明してください。法律の助言はしません。

## 守ること

- 映像は、自分の機械のモデルで見ます。Ollama でも、クラウドのモデル名(gemma4 の `cloud` の
  タグなど)を渡すとクラウドに送られるので使いません
- 詳しく見たい場面の静止画だけは、入力を学習に使わない API(Claude、OpenAI、有料枠の Gemini)に
  送ってかまいません。消費者向けのアプリ(gemini.google.com、claude.ai、chatgpt.com)には
  送りません。外の AI に人を割り出させません(3 社とも、同意のない監視や顔認識を禁じています)。
  人が映っていない場面(動物など)は、人の情報を含まないので問題が少なくなります
- 顔の画像と顔の特徴のデータは、自分の機械でだけ扱います
- 映像と顔のデータを、AI への依頼(このリポジトリの作業を含む)に貼りません
- モデルは、ライセンスで使い方が許されている物を使います(下の表)。住人が自分の家で使うのは
  商用ではありません。見守りを有料のサービスとして出すときは、商用で使えるかを確かめます
- 顔の特徴のデータは個人識別符号で、個人情報です。顔で人を見分けることは、外から見て分からない
  ので、利用目的として通知か公表が要ります
- 顔を登録するのは、同意した人だけにします(家族、住人)。登録していない人の顔の特徴の
  データは残しません

## 調べること

自分の家で家族のために使うだけなら、個人情報保護法の義務はかかりません。仕事として使うとき(空き家の
見守りを請ける、集合住宅を管理する)は、カメラの掲示、映像の保存の期間、顔認識の使い方、管理組合の
決め方を、個人情報保護法と個人情報保護委員会の資料、マンションの標準管理規約の、その時点の物で調べ、
作りに入れます。

## 使う物

| 役目 | 物 | ライセンス |
|---|---|---|
| 録画と物の検出 | Frigate v0.18.0 | MIT |
| VLM を動かす | Ollama(か OpenAI 互換の API を出す物) | MIT |
| 顔の検出と認識 | OpenCV Zoo の YuNet と SFace | MIT、Apache-2.0 |

### モデル(2026-09-29 に確かめた)

いまは、画像も読める汎用のモデルが使えます(Frigate の説明書も qwen3.6 と qwen3.8 を勧めて
います)。画像専用の Qwen3-VL も使えます。

住人が自分の家で使うのは商用ではないので、モデルの費用はかかりません。見守りを有料の
サービスとして出すのは商用です。商用で使えるモデルを選び、モデルに費用がかかるなら、
機械、電気、回線と一緒に料金に含めて考えます。

| モデル | ライセンス | 自分の家で | 有料のサービスで | 商用の費用と条件、注意 |
|---|---|---|---|---|
| Qwen3.5、Qwen3.6、Qwen3.8-27B(汎用。画像も読める) | Apache-2.0 | 使える | 使える | 無料。利用規約の上乗せなし |
| Gemma 4(汎用。画像も読める) | Apache-2.0 | 使える | 使える | 無料。利用規約の上乗せなし |
| Qwen3-VL(画像専用) | Apache-2.0 | 使える | 使える | 無料。利用規約の上乗せなし |
| Qwen2.5-VL-72B | Qwen License | 使える | 使える | 無料。月の利用者が 1 億人を超えたら許可が要る |
| Cosmos-Reason2(2B、8B、32B)、Nemotron Nano 12B v2 VL(NVIDIA) | NVIDIA Open Model License | 使える | 使える | 無料。禁じているのは違法な監視と、法が同意を求めるときの同意のない生体情報の処理。安全の仕組み(ガードレール)を外すと権利が切れる。Cosmos は「Built on NVIDIA Cosmos」の表示が要る |

### 顔認識のモデル

| モデル | 自分の家で | 有料のサービスで | 注意 |
|---|---|---|---|
| OpenCV Zoo の YuNet と SFace | 使える | 使える | 重みまで MIT と Apache-2.0 |

- Frigate は、VLM を CPU で動かすことを勧めていません。Nvidia の GPU か、Intel の iGPU や NPU
  (OpenVINO)などを使います。7B の 4bit のモデルなら、たいてい 8GB の VRAM に入ります

## 手順

1. 何を見たいかを聞きます
   * 個人の住宅: 家族の出入り、来客、配達、留守の間の出来事
   * 空き家: 人が入った、窓や扉が開いた、変わりがないか。見に行く回数を減らしたいか
   * 集合住宅の共用玄関: 出入り、共連れ、荷物、夜の出入り
   * 顔認識が要るか(家族を見分けて、知らせを減らすなど)
2. 共用玄関なら、管理組合の決議と使用細則を確かめます。仕事として請けるなら、掲示と公表を
   書きます(撮っていること、運用する者、目的、問い合わせ先、保存の期間。説明文を残すことと
   顔認識をするなら、そのことも)
3. 機械を用意します。Linux の PC に Frigate を入れ、カメラ(RTSP)をつなぎます。映像は
   その PC の中に置きます。ダウンロード(Frigate、モデル)は、名前、出どころ、大きさを伝えて
   許しを得てからにします
   * 空き家は、ネットの回線と電気が要ります。回線とルーターは [network](../network/) で組めます。
     外から見るときは、WireGuard の VPN を通し、カメラと Frigate を直に外に開けません
4. VLM をつなぎます。同じ PC か同じ家の中の機械で Ollama を動かし、Frigate の GenAI の提供者に
   します。カメラごとのプロンプトに、何を普段の動きとするか(家族の出入り、配達、空き家なら
   人がいないのが普段)を書きます。空き家は、1 日の要約を作らせると、見に行かなくても様子が
   分かります。手元のモデルが気になると判断した場面は、静止画で外の API に詳しく見てもらえます
   (Frigate は Gemini と OpenAI をそのまま使えます。Claude は OpenAI 互換の窓口か、自分の
   プログラムから呼びます)
5. 顔認識を入れるなら、登録するのは同意した家族や住人だけにし、登録していない人の顔の
   データは残さない設定にします。住人が出たら、その顔を消します
6. 知らせを付けます。Frigate のイベント(MQTT か API)を受けて、持ち主のスマートフォンに
   知らせます([tsuuchi](../tsuuchi/) の Web Push かメール。自分のサーバーに置ける ntfy なら、
   Frigate のイベントから `curl` 1 行でスマートフォンに送れます)。鍵を付けているなら、開け閉めの
   記録と合わせて見られます([kagi](../kagi/))。決めるのは人で、AI の説明は手がかりです
7. 保存の期間を決め、過ぎた録画と説明文を消します

## 出典

- 個人情報保護委員会「ガイドライン(通則編)」(https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/)、
  「Q&A」(https://www.ppc.go.jp/personalinfo/faq/APPI_QA/)1-12〜1-15、1-41、5-4、10-8
- 個人情報保護委員会「犯罪予防や安全確保のための顔識別機能付きカメラシステムの利用について」
  (https://www.ppc.go.jp/files/pdf/230329_gidai2.pdf)
- 個人情報の保護に関する法律施行令第 1 条、施行規則第 2 条(https://laws.e-gov.go.jp/law/428M60020000003)
- 国交省「マンション標準管理規約(単棟型)コメント」(https://www.mlit.go.jp/jutakukentiku/house/content/001999022.pdf)
- 個人情報の保護に関する法律(https://laws.e-gov.go.jp/law/415AC0000000057)第 16 条第 2 項
- Frigate(https://github.com/blakeblackshear/frigate)v0.18.0。説明書の GenAI
  (https://docs.frigate.video/configuration/genai/genai_config)、機械(https://docs.frigate.video/frigate/hardware)
- Ollama(https://github.com/ollama/ollama)。Qwen のモデルのカード(https://huggingface.co/Qwen/Qwen3.8-27B、
  https://huggingface.co/Qwen/Qwen3.6-27B、https://huggingface.co/Qwen/Qwen3.5-27B、
  https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct)と、Qwen License
  (https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct/blob/main/LICENSE)
- Gemma 4 のライセンス(https://ai.google.dev/gemma/apache_2)
- NVIDIA Open Model License(https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/)、
  Trustworthy AI terms(https://www.nvidia.com/en-us/agreements/trustworthy-ai/terms/)、
  Cosmos-Reason2(https://huggingface.co/nvidia/Cosmos-Reason2-32B)、Nemotron Nano VL
  (https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL-BF16)
- OpenCV Zoo の YuNet(https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)と
  SFace(https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface)
- Gemini API の追加の利用規約(https://ai.google.dev/gemini-api/terms)、Google の生成 AI の禁止用途の
  方針(https://policies.google.com/terms/generative-ai/use-policy)。Anthropic の利用ポリシー
  (https://www.anthropic.com/legal/aup)と商用版の学習(https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)。
  OpenAI のデータの扱い(https://developers.openai.com/api/docs/guides/your-data)。Anthropic の
  OpenAI SDK 互換(https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)。2026-10-06 に確かめました
- ntfy(https://docs.ntfy.sh/、https://github.com/binwiederhier/ntfy)v2.28.0、Apache-2.0 と GPL-2.0

2026-10-06 に見直しました(条文とライセンスは 2026-09-29 に確かめた)。
