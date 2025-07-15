import pyxel
from PIL import Image
import warnings
import os

DEBUG = False

class PyxelImageResource:
    """
    個々の画像リソースを管理するクラス。
    画像の読み込み、パレットの保持、描画機能を提供します。
    """
    @staticmethod
    def _get_png_size_pil(file_path):
        """
        PILライブラリを使用してPNG画像のサイズを取得する静的メソッド。
        
        Args:
            file_path (str): PNG画像ファイルのパス
        
        Returns:
            tuple: (width, height) の形式でサイズを返す。エラーの場合は (None, None) を返す。
        
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            IOError: ファイル読み込みエラーが発生した場合
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                return (width, height)
        
        except FileNotFoundError:
            print(f"エラー: ファイル '{file_path}' が見つかりません。")
            return None, None
        except IOError as e:
            print(f"画像読み込みエラー: {e}")
            return None, None
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return None, None

    def __init__(self, filename, palette_offset=0):
        """
        PyxelImageResourceのコンストラクタ。
        画像を読み込み、パレット情報を抽出し、Pyxelイメージを作成します。

        Args:
            filename (str): 画像ファイル名
            palette_offset (int): 結合パレット内でのこの画像のパレットの開始インデックス
        """
        try:
            with Image.open(filename) as img:
                # 画像に透過情報が含まれているか確認
                self.has_transparency = 'transparency' in img.info or img.mode == 'RGBA'
                if DEBUG:
                    colors = img.getcolors()
                    num_colors = len(colors) if colors else 0
                    print(f"DEBUG: {filename} - ColorType: {img.mode}, Colors: {num_colors}, has_transparency: {self.has_transparency}")
                size_x, size_y = img.size
        except (FileNotFoundError, IOError) as e:
            raise ValueError(f"画像を読み込めませんでした: {filename} - {e}")

        self.image = pyxel.Image(size_x, size_y)
        # 画像とそのパレットを読み込む。この処理は一時的にpyxel.colorsを上書きする
        self.image.load(0, 0, filename, incl_colors=True)
        # 読み込んだ画像からパレットをリストとして保存
        self.palette = pyxel.colors.to_list()

        if DEBUG:
            hex_palette = [f"#{c:06x}" for c in self.palette]
            print(f"DEBUG: {filename} - 生成されたパレットの色数: {len(self.palette)}, パレット: {hex_palette}")

        # 透過色としてパレットの最初の色を使用
        self.transparent_color = palette_offset

        # パレットオフセットに基づいてピクセルの色インデックスを調整
        if palette_offset > 0:
            for x in range(size_x):
                for y in range(size_y):
                    color = self.image.pget(x, y)
                    self.image.pset(x, y, color + palette_offset)

    def draw(self, x, y, u=0, v=0, transparency_enabled=True):
        """
        この画像リソースを画面に描画する。

        Args:
            x (int): 描画先のX座標
            y (int): 描画先のY座標
            u (int): 元画像のX座標
            v (int): 元画像のY座標
            transparency_enabled (bool): 透過を有効にするか
        """
        if self.has_transparency and transparency_enabled:
            # 透過色を指定して描画
            pyxel.blt(x, y, self.image, u, v, self.image.width, self.image.height, self.transparent_color)
        else:
            # 透過なしで描画
            pyxel.blt(x, y, self.image, u, v, self.image.width, self.image.height)

class ImageManager:
    """
    複数の画像を管理し、それらのパレットを自動的に結合するクラス。
    'with'ステートメントでの使用を想定しています。
    """
    def __init__(self):
        """ImageManagerのコンストラクタ。"""
        self.combined_palette = pyxel.colors.to_list()  # 結合されたパレット
        self.images = {}  # 読み込んだ画像リソースを保持する辞書
        self._dirty = False  # パレットが変更されたかを示すフラグ

    def load_image(self, filename):
        """
        画像を読み込み、パレットを管理し、PyxelImageResourceオブジェクトを返す。
        
        Args:
            filename (str): 画像ファイル名
        
        Returns:
            PyxelImageResource: 生成された画像リソース
        
        Raises:
            ValueError: パレット数の上限を超えるなど、読み込みに失敗した場合
        """
        # クラッシュを避けるために、パレットサイズを事前にチェック
        try:
            # 一時的なPyxelイメージに読み込む
            with Image.open(filename) as pil_img:
                temp_img = pyxel.Image(pil_img.width, pil_img.height)
                # 画像とパレットを読み込む（pyxel.colorsが一時的に上書きされる）
                temp_img.load(0, 0, filename, incl_colors=True)
                # 読み込んだ画像からパレットを保存
                image_palette = pyxel.colors.to_list()
        except Exception as e:
            raise ValueError(f"パレットチェックのための画像プリロードに失敗しました: {filename} - {e}")

        # 結合後のパレット数が255色を超えるかチェック
        if len(self.combined_palette) + len(image_palette) > 255:
            # 一時的な読み込みで上書きされたグローバルパレットを元に戻す
            pyxel.colors.from_list(self.combined_palette)
            raise ValueError(f"{filename} を追加するとパレットの上限255色を超えてしまいます")
        
        # 新しい画像リソースを作成
        palette_offset = len(self.combined_palette)
        resource = PyxelImageResource(filename, palette_offset)
        
        # パレットと画像リソースをマネージャーに追加
        self.combined_palette.extend(resource.palette)
        self.images[filename] = resource
        self._dirty = True
        
        return resource

    def apply_palette_to_pyxel(self):
        """最終的に結合されたパレットをPyxelに適用する。"""
        if self._dirty:
            pyxel.colors.from_list(self.combined_palette)
            self._dirty = False

    def __enter__(self):
        """'with'ステートメントの開始時に呼び出される。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """'with'ステートメントの終了時に呼び出され、パレットを適用する。"""
        self.apply_palette_to_pyxel()

    def __del__(self):
        """インスタンス破棄時の処理。"""
        # インスタンス破棄時に_dirtyフラグがTrueなら、パレットが適用されていない
        if self._dirty:
            warnings.warn(
                "ImageManagerが正しく終了されませんでした。"
                "'with'ステートメントを使用してパレットが適用されるようにしてください。",
                ResourceWarning
            )
