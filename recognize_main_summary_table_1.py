'''
「検査陽性者の状況」画像から数値データを抽出する処理 パターン１
'''

import re

import pytesseract
import cv2

def recognize(jpg_path):
    src = cv2.imread(str(jpg_path))
    img = cv2.inRange(src, (150, 120, 130), (255, 255, 255))

    # 範囲指定
    img_crop = img[0:550]
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img_crop, lang="jpn", config="--psm 3").replace(".", "").replace(",", "")
    print(txt)

    # xx人 な箇所を全て抜き出す
    data = list(map(lambda str:int(str.replace('人', '')), re.findall("[0-9]+人", txt.replace(',', ''))))
    return data
