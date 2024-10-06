import pyautogui
import time
from PIL import Image, ImageFilter
import pytesseract
import os
import pygetwindow as gw
import numpy as np
import matplotlib.pyplot as plt


# 定数の定義
START_PAGE = 1
TOTAL_PAGES = 569  # 処理するページ数
WAIT_TIME = 1  # ページ遷移の待機時間（秒）

# distフォルダを作成（存在しない場合）
os.makedirs("dist", exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def focus_kindle_window():
    kindle_windows = gw.getWindowsWithTitle("Kindle for")
    if kindle_windows:
        kindle_window = kindle_windows[0]
        kindle_window.activate()
        kindle_window.maximize()
        time.sleep(1)
        pyautogui.press("f11")
        time.sleep(5)
    else:
        raise Exception("Kindleウィンドウが見つかりません。")


def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join("dist", f"screenshot_{time.time()}.png")
    screenshot.save(screenshot_path)
    return screenshot_path


def process_image_with_ocr(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img, lang="jpn")
    return text


def next_page():
    pyautogui.press("right")


def crop_white_center(
    input_path, page_no, threshold=200, edge_enhance=True, debug=True
):
    # 画像を開く
    img = Image.open(input_path)
    img_width, img_height = img.size

    # 手動で指定された領域で初期切り抜き
    left, top, right, bottom = (500, 0, img_width - 500, img_height)
    img_cropped = img.crop((left, top, right, bottom))

    # グレースケールに変換
    gray = img_cropped.convert("L")

    # NumPy配列に変換
    img_array = np.array(gray)

    # 白い部分（閾値以上）を見つける
    white_pixels = np.where(img_array > threshold)

    if len(white_pixels[0]) > 0 and len(white_pixels[1]) > 0:
        # 白い部分の境界を取得
        crop_top, crop_left = np.min(white_pixels[0]), np.min(white_pixels[1])
        crop_bottom, crop_right = np.max(white_pixels[0]), np.max(white_pixels[1])

        # 余白を追加
        margin = 10
        crop_top = max(0, crop_top - margin)
        crop_bottom = min(img_array.shape[0], crop_bottom + margin)
        crop_left = max(0, crop_left - margin)
        crop_right = min(img_array.shape[1], crop_right + margin)
    else:
        print(
            "白い領域が検出されませんでした。手動で切り抜いた画像をそのまま使用します。"
        )
        crop_top, crop_left, crop_bottom, crop_right = (
            0,
            0,
            img_array.shape[0],
            img_array.shape[1],
        )

    # デバッグ情報（オプション）
    if debug:
        plt.figure(figsize=(15, 10))
        plt.subplot(221)
        plt.imshow(img_array, cmap="gray")
        plt.title("Manual Cropped Grayscale Image")
        plt.subplot(222)
        plt.imshow(img_array > threshold, cmap="binary")
        plt.title(f"Binary Image (threshold={threshold})")
        plt.subplot(223)
        plt.hist(img_array.ravel(), bins=256, range=(0, 256))
        plt.axvline(threshold, color="r", linestyle="dashed", linewidth=2)
        plt.title("Histogram and Threshold")
        plt.subplot(224)
        plt.imshow(img_array, cmap="gray")
        plt.plot(
            [crop_left, crop_right, crop_right, crop_left, crop_left],
            [crop_top, crop_top, crop_bottom, crop_bottom, crop_top],
            "r-",
        )
        plt.title("Detected Region")
        plt.tight_layout()
        plt.savefig("debug_output.png")
        print(
            f"Final cropping coordinates: Top={crop_top}, Left={crop_left}, Bottom={crop_bottom}, Right={crop_right}"
        )

    # 検出された白い領域を切り抜く
    final_img = img_cropped.crop((crop_left, crop_top, crop_right, crop_bottom))

    # 切り抜いた画像を保存
    output_path = os.path.join("dist", f"{page_no}.png")
    final_img.save(output_path)


def main():
    try:
        focus_kindle_window()

        for i in range(TOTAL_PAGES):
            print(f"処理中: ページ {i+1}/{TOTAL_PAGES}")

            screenshot_path = take_screenshot()
            manual_crop = (500, 0, 2500, 1800)
            crop_white_center(
                screenshot_path,
                START_PAGE + i,
                threshold=180,
                edge_enhance=True,
                debug=False,
            )
            os.remove(screenshot_path)

            if i < TOTAL_PAGES - 1:  # 最後のページでない場合のみ次のページへ
                next_page()
                time.sleep(WAIT_TIME)  # ページ遷移を待つ

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    finally:
        pyautogui.press("f11")  # フルスクリーンモードを解除


if __name__ == "__main__":
    main()
