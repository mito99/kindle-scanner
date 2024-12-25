import os
from PIL import Image
import pytesseract
import glob
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def png_to_txt(input_dir, output_file):
    # distディレクトリ内のすべてのPNG画像を取得
    image_files = sorted(glob.glob("dist/*.png"))
    png_files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith(".png")],
        key=lambda x: int(x.split(".")[0]),
    )
    # 各画像を処理し、テキストを抽出
    with open(output_file, "w", encoding="utf-8") as f:
        for png_file in png_files:
            # 画像を開く
            with Image.open(os.path.join(input_dir, png_file)) as img:
                # 画像からテキストを抽出
                text = pytesseract.image_to_string(img, lang="jpn")

                # ファイル名（ページ番号）を取得
                page_number = os.path.splitext(os.path.basename(png_file))[0]

                # 抽出したテキストをファイルに書き込む
                f.write(f"===== Page {page_number} =====\n")
                f.write(clean_ocr_text(text))
                f.write("\n\n")
    print(f"テキスト抽出が完了しました。結果は {output_file} に保存されました。")


def clean_ocr_text(text):
    # 行ごとに処理
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        # 行の先頭と末尾の空白を削除
        line = line.strip()

        # 連続する空白を1つに置換
        line = re.sub(r"\s+", " ", line)

        # 日本語文字の間の空白を削除
        line = re.sub(
            r"(?<=[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])\s+(?=[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])",
            "",
            line,
        )

        cleaned_lines.append(line)

    # 処理した行を改行で結合
    return "\n".join(cleaned_lines)


def main():
    # png_to_txt("dist", "output.txt")

    with open("new_output.txt", "w", encoding="utf-8") as fw:
        with open("output.txt", "r", encoding="utf-8") as fr:
            fw.write(clean_ocr_text(fr.read()))


if __name__ == "__main__":
    main()
