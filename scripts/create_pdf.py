from PIL import Image
import os

from tqdm import tqdm


def png_to_pdf(input_dir, output_pdf):
    # 入力ディレクトリ内のPNGファイルをソートしてリスト化
    png_files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith(".png")],
        key=lambda x: int(x.split(".")[0]),
    )

    # 最初の画像を開く
    images = []
    for png_file in tqdm(png_files):
        image = Image.open(os.path.join(input_dir, png_file))
        if image.mode == "RGBA":
            image = image.convert("RGB")
        images.append(image)

    # 最初の画像を使ってPDFを作成し、残りの画像を追加
    images[0].save(output_pdf, save_all=True, append_images=images[1:])


# 使用例
png_to_pdf("dist/image", "dist/pdf/output.pdf")
