# title: Pyxel Image Helper サンプル
# author: daraddara5656
# desc: Pyxel Image Helperの機能を示すサンプルプログラム

import pyxel
import glob
import os
from pyxel_image_helper import ImageManager

class App:
    """アプリケーション本体のクラス"""
    def __init__(self):
        """初期化処理"""
        pyxel.init(320, 320, title="Pyxel Image Helper Sample", fps=30)

        # 描画する画像リソースのリスト
        self.images_to_draw = []
        # ImageManagerを使用して画像を読み込む
        with ImageManager() as image_manager:
            # imgフォルダ内のpngファイルをすべて取得
            png_files = sorted(glob.glob('img/*.png'))
            for filename in png_files:
                # ファイル名が'_'で始まるものはスキップ
                if os.path.basename(filename).startswith('_'):
                    continue
                try:
                    # 画像を読み込み、パレットを管理
                    resource = image_manager.load_image(filename)
                    self.images_to_draw.append(resource)
                except ValueError as e:
                    # パレット数の上限を超えるなどのエラーが発生した場合はスキップ
                    print(f"エラーのためファイルをスキップします: {e}")

        # 背景色のアニメーション関連の変数
        self.bg_color_index = 0  # 現在の背景色
        self.bg_color_timer = 0  # 表示状態を切り替えるためのタイマー
        self.transparency_enabled = True  # 透過色の有効/無効
        self.display_state = 0  # 現在の表示状態 (0-3)

        pyxel.run(self.update, self.draw)

    def update(self):
        """更新処理"""
        # Qキーでアプリケーションを終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # 3秒ごと（90フレーム）に表示状態を更新
        self.bg_color_timer += 1
        if self.bg_color_timer >= 90:
            self.bg_color_timer = 0
            self.display_state = (self.display_state + 1) % 4

            # 表示状態に応じて背景色と透過設定を切り替える
            if self.display_state == 0:
                # 背景色: 黒, 透過: ON
                self.bg_color_index = 0
                self.transparency_enabled = True
            elif self.display_state == 1:
                # 背景色: 白, 透過: ON
                self.bg_color_index = 7
                self.transparency_enabled = True
            elif self.display_state == 2:
                # 背景色: 黒, 透過: OFF
                self.bg_color_index = 0
                self.transparency_enabled = False
            elif self.display_state == 3:
                # 背景色: 白, 透過: OFF
                self.bg_color_index = 7
                self.transparency_enabled = False

    def draw(self):
        """描画処理"""
        # 指定した色で画面をクリア
        pyxel.cls(self.bg_color_index)

        # 画像を並べて描画するための変数
        margin = 4  # 画像間のマージン
        x, y = margin, margin
        row_height = 0  # 現在の行の高さ
        
        for resource in self.images_to_draw:
            # 画像が画面幅を超える場合は改行
            if x + resource.image.width > pyxel.width - margin:
                x = margin
                y += row_height + margin
                row_height = 0

            # 画像を描画
            resource.draw(x, y, transparency_enabled=self.transparency_enabled)
            
            # 次の画像の描画位置を更新
            x += resource.image.width + margin
            # 現在の行で最も高い画像の高さを保持
            if resource.image.height > row_height:
                row_height = resource.image.height

if __name__ == "__main__":
    App()
