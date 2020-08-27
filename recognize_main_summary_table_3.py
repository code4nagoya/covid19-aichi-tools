'''
「検査陽性者の状況」画像から数値データを抽出する処理 パターン１
'''

import re

import pytesseract
import cv2
import numpy as np

# 画像内の矩形を抽出
# https://stackoverflow.com/a/60068297
def cropTable(src):

    hei = src.shape[0]
    wid = src.shape[1]
    totalArea = wid * hei

    original = src.copy()
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours, obtain bounding box, extract and save ROI
    ROI_number = 0
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    maxArea = 0
    maxNo = -1
    maxX = -1
    maxY = -1
    maxW = -1
    maxH = -1
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(src, (x, y), (x + w, y + h), (36,255,12), 2)
        ROI = original[y:y+h, x:x+w]
        # cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)

        # 面積が最大の矩形を記憶（ただし画像全体を覆う矩形は除外）
        area = w * h
        if maxArea < area and (totalArea * 0.9) > area :
            maxNo = ROI_number
            maxArea = area
            maxX = x
            maxY = y
            maxW = w
            maxH = h

        ROI_number += 1

    # 面積最大の矩形内を抽出（ついでに枠線を消すために 3pixel オフセット）
    img = original[maxY+int((maxH/4)*3):maxY+maxH, maxX+3:maxX+maxW-6]
    return img

# 拡大と白黒化
def grayAndResize(src):
    neiborhood24 = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ],
        np.uint8,
    )

    height = src.shape[0]
    width = src.shape[1]

    dilated = cv2.dilate(src, neiborhood24, iterations=1)
    diff = cv2.absdiff(dilated, src)
    contour = 255 - diff

    gray2 = cv2.resize(contour, (int(width * 2), int(height * 2)))
    th, img = cv2.threshold(gray2, 180, 255, cv2.THRESH_BINARY)
    return img

def recognize(jpg_path):
    src = cv2.imread(str(jpg_path))
    hei = src.shape[0]
    wid = src.shape[1]

    # 画像の上25%でカット
    img = src[0:int(hei * 0.25)]
    # cv2.imwrite('table_ptn3_1_cropped.jpg', img)

    # 画像内の矩形を抽出
    img = cropTable(img)
    # cv2.imwrite('table_ptn3_2_rected.jpg', img)

    # 拡大と白黒化
    img = grayAndResize(img)
    # cv2.imwrite('table_ptn3_3_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789").replace(".", "").replace(",", "")
    print(txt)

    # xx人 な箇所を全て抜き出す
    data = list(map(lambda str:int(str.replace('人', '')), re.findall("[0-9]+", txt)))
    return data
