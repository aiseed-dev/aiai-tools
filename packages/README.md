# パッケージ

aiai tools のスキルで作った物のうち、ほかのアプリでも使える部品を、パッケージとして置きます。
どれも MIT で、パッケージごとに PyPI に出します(タグ `<名前>-v<版>` を push すると、
`.github/workflows/publish-<名前>.yml` が出します)。

| パッケージ | 中身 |
|---|---|
| [flet-gpumap](flet-gpumap/) | GPU で格子データ(気象の予報など)を地図に描く Flet の拡張。地図とグラフに広げる |
