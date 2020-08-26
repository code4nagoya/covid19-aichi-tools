'''
「検査陽性者の状況」画像から注記を抽出する処理 パターン２
'''

import re
import pytesseract
import cv2

def recognize(jpg_path):
    src = cv2.imread(str(jpg_path))
    hei = src.shape[0]
    wid = src.shape[1]

    # 画像の上25%～50%でカット
    src = src[int(hei * 0.25):int(hei * 0.5)]
    # cv2.imwrite('remarks_ptn2_1_cropped.jpg', src)

    # 拡大と白黒化
    height = src.shape[0]
    width = src.shape[1]
    img = cv2.resize(src, (int(width * 2), int(height * 2)))
    # img = cv2.inRange(tmp, (145, 125, 110), (255, 255, 255))
    # cv2.imwrite('remarks_ptn2_2_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 11").replace(".", "").replace(",", "")
    print(txt)

    # ※1 ※2 または (注) で始まる文を抽出
    remarks = re.findall("^(.?\d{1} .*|\(注.* .*)$", txt, re.M)
    
    def normalize(txt):
        # 行頭の ※1 ※2 や (注) を削除（空白以降を抽出）
        txt = txt[txt.find(' ') + 1:]
        # 空白を除去
        txt = txt.replace(' ', '')
        # 画像切れて認識できない「掲載。」を補完
        txt = re.sub('検査を行ったものについて掲.*$', '検査を行ったものについて掲載。', txt)
        return txt

    remarks = list(map(normalize, remarks))
    return remarks
