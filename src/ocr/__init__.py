from PIL import Image
import pyocr
import pyocr.builders
import cv2
import numpy as np

from dotenv import load_dotenv
load_dotenv()


def render_doc_text(file_path):

    # ツール取得
    pyocr.tesseract.TESSERACT_CMD = 'C:/Users/hi_tu/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'
    tools = pyocr.get_available_tools()
    tool = tools[0]

    # 画像取得
    img = cv2.imread(file_path, 0)
    img = Image.fromarray(img)

    # OCR
    builder = pyocr.builders.TextBuilder()
    result = tool.image_to_string(img, lang="jpn", builder=builder)

    # 結果から空白文字削除
    data_list = [text for text in result.split('\n') if text.strip()]
    data_list

    return data_list