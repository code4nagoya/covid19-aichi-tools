'''
「検査陽性者の状況」画像から数値データを抽出する処理 パターン１
'''

import re

import pytesseract
import cv2

def recognize(jpg_path):
    src = cv2.imread(str(jpg_path))
    hei = src.shape[0]
    wid = src.shape[1]

    # 画像の上25%でカット
    src = src[0:int(hei * 0.25)]
    totalArea = wid * int(hei / 4)
    cv2.imwrite('table_ptn1_1_cropped.jpg', src)

    # 画像内の矩形を抽出
    # https://stackoverflow.com/a/60068297
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
    src = src[maxY+int((maxH/4)*3):maxY+maxH, maxX+3:maxX+maxW-6]
    cv2.imwrite('table_ptn1_2_rected.jpg', src)

    # 拡大と白黒化
    height = src.shape[0]
    width = src.shape[1]
    tmp = cv2.resize(src, (int(width * 2), int(height * 2)))
    img = cv2.inRange(tmp, (145, 125, 110), (255, 255, 255))
    cv2.imwrite('table_ptn1_3_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789").replace(".", "").replace(",", "")
    print(txt)

    # xx人 な箇所を全て抜き出す
    data = list(map(lambda str:int(str.replace('人', '')), re.findall("[0-9]+人", txt.replace(',', ''))))
    return data
