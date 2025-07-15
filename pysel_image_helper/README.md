# Pyxel Image Helper

`Pyxel Image Helper` は、レトロゲームエンジン [Pyxel](https://github.com/kitao/pyxel) で複数の画像を使用する際に、それぞれの画像が持つカラーパレットを自動的に結合・管理するためのヘルパーライブラリです。

Pyxelは通常、グローバルな16色のカラーパレットを使用しますが、このライブラリを使うことで、複数の画像（それぞれが異なるパレットを持つ）を読み込み、それらのパレットを最大255色まで結合して利用できます。

## 主な機能

- **パレットの自動結合**: 複数の画像ファイルを読み込むと、それぞれのパレットを自動で結合し、Pyxelのグローバルパレットに設定します。
- **最大255色のサポート**: Pyxelのパレット上限である255色まで、動的に色を追加できます。
- **透過色のサポート**: PNG画像の透過情報を維持したまま描画できます。
- **シンプルなAPI**: `with`ステートメントを使って、直感的に画像リソースを管理できます。

## ファイル構成

```
pysel_image_helper/
├── pyxel_image_helper.py   # ライブラリ本体
├── sample.py               # 使用例を示すサンプルコード
├── README.md               # このファイル
└── img/                    # サンプル用の画像ファイル
    ├── ...
    └── ...
```

## 使い方

`ImageManager`を`with`ステートメントでインスタンス化し、`load_image()`メソッドで画像を読み込みます。`with`ブロックを抜ける際に、結合されたパレットが自動的にPyxelに適用されます。

```python
import pyxel
from pyxel_image_helper import ImageManager

class App:
    def __init__(self):
        pyxel.init(320, 320, title="Sample")

        self.images_to_draw = []
        # ImageManagerを使用して画像を読み込む
        with ImageManager() as image_manager:
            try:
                # 画像を読み込み、リソースを取得
                self.player_img = image_manager.load_image("img/yuusha.png")
                self.enemy_img = image_manager.load_image("img/dragon.png")
                
                self.images_to_draw.append(self.player_img)
                self.images_to_draw.append(self.enemy_img)

            except ValueError as e:
                # パレット数の上限(255色)を超えた場合のエラーハンドリング
                print(f"エラー: {e}")

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        
        # 読み込んだ画像を描画
        self.player_img.draw(10, 10)
        self.enemy_img.draw(50, 50)

App()
```

### 注意点

- 結合後の合計パレット数が255色を超えると`ValueError`が発生します。
- `ImageManager`は`with`ステートメントと共に使用してください。これにより、リソース管理とパレットの適用が正しく行われます。

## クラスとメソッド

### `ImageManager`

複数の画像リソースとパレットを管理するメインクラス。

- `load_image(filename)`
  - 画像ファイルを読み込み、パレットを結合し、`PyxelImageResource`オブジェクトを返します。
  - **引数**:
    - `filename` (str): 画像ファイルのパス。
  - **戻り値**:
    - `PyxelImageResource`: 描画や情報取得に使うリソースオブジェクト。
  - **例外**:
    - `ValueError`: パレットの合計が255色を超える場合に発生します。

### `PyxelImageResource`

個々の画像リソースを管理するクラス。`ImageManager`によって生成されます。

- `draw(x, y, transparency_enabled=True)`
  - 画像をPyxelの画面に描画します。
  - **引数**:
    - `x` (int): 描画先のX座標。
    - `y` (int): 描画先のY座標。
    - `transparency_enabled` (bool): `True`の場合、画像の透過色を有効にして描画します。
