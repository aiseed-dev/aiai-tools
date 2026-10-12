# aiai_ja(Tryton 8.0 の日本語)

Tryton には日本語の訳がありません。これは、Tryton 8.0 の画面を日本語にする物です。言語 `ja` を
作り、有効にしたモジュールの訳を読み込み、Web の画面(sao)の訳を置きます。Tryton の本体には
手を入れません。

訳したのは、次のモジュールと sao の、すべての文です(2026-10-12。モジュールの文は 2,868、sao は 269)。

ir、res、account、account_invoice、account_invoice_stock、account_product、company、country、
currency、party、product、purchase、sale、stock

訳は AI が下書きした物で、まだ人が全部を読んではいません。おかしな訳は直してください。

## 入れ方

Tryton 8.0 の Python で入れ、データベースに読み込みます。読み込んだら trytond を動かし直し、
利用者の設定で言語を「日本語」にします。

```
pip install /リポジトリの場所/tryton/aiai_ja
trytond_import_ja -c trytond.conf -d tryton --sao /sao の場所
```

モジュールを足したときは、`trytond_import_ja` をもう一度動かします。

## 訳を直す、足す

訳は [yaku.csv](yaku.csv) にあります。英語の文ごとに 1 行で、`module` が空なら全部のモジュールに、
`stock` などを書けばそのモジュールだけに使います(会計の Move は「仕訳」、在庫の Move は「移動」)。
言葉は、[用語集](yougo.csv)と ERPNext の用語集([erpnext/aiai_ja/yougo.csv](../../erpnext/aiai_ja/yougo.csv))
にそろえます。

直したら、PO ファイルを作り直します。差し込み(`%(name)s`、`%s`、`{0}`、`${...}`)と HTML の印の
数が英語と違うと、知らせて止まります。

```
python tsukuru.py /sao の場所
```

訳のないモジュールを足すときは、そのモジュールを入れてから `tsukuru.py` を動かし、訳の無い文を
`yaku.csv` に足します。

## ライセンス

GPL-3.0-or-later です(Tryton と同じ)。Tryton の公式の訳(Weblate)に出すこともできます。
