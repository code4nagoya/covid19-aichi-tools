'''
「検査陽性者の状況」画像から注記を抽出する処理 パターン２
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

    lst = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(src, (x, y), (x + w, y + h), (36,255,12), 2)
        ROI = original[y:y+h, x:x+w]
        # cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)

        # 面積が最大の矩形を記憶（ただし画像全体を覆う矩形は除外）
        area = w * h
        if (totalArea * 0.9) > area:
            lst.append((ROI_number, area, x, y, w, h))

        ROI_number += 1

    # 矩形面積の降順に並び替え
    lst.sort(key=lambda x:-x[1])

    # 1番目：「クラスターの感染」、2番目：「○月～」なハズなので
    # 2番目の y+h から 1番目の y までを切りだす
    first = lst[0]
    scond = lst[1]
    top = (scond[3]+scond[5])
    bottom = first[3]

    if top >= bottom:
        print("注記位置を特定できませんでした")
        return src

    img = original[top:bottom]
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

    # 画像の上25%～60%でカット
    img = src[int(hei * 0.25):int(hei * 0.6)]
    # cv2.imwrite('remarks_ptn2_1_cropped.jpg', img)

    # 画像内の矩形を抽出
    img = cropTable(img)
    # cv2.imwrite('remarks_ptn2_2_rected.jpg', img)

    # 拡大と白黒化
    img = grayAndResize(img)
    # cv2.imwrite('remarks_ptn2_3_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 11").replace(".", "").replace(",", "")
    print(txt)

    # ※1 ※2 または (注) で始まる文を抽出
    remarks = re.findall("^(.*?\d{1} .*|\(.?.* .*)$", txt, re.M)
    
    def normalize(txt):
        # 行頭の ※1 ※2 や (注) を削除（空白以降を抽出）
        txt = txt[txt.find(' ') + 1:]
        # 空白を除去
        txt = txt.replace(' ', '')
        # 画像切れて認識できない「掲載。」を補完
        txt = re.sub('検査を行ったものについて掲.*$', '検査を行ったものについて掲載。', txt)
        return txt

    remarks = list(map(normalize, remarks))
    print(remarks)
    return remarks
