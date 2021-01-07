'''
「検査陽性者の状況」画像から更新日を抽出する処理 パターン2
'''
import re
import pytesseract
import cv2
from datetime import datetime, timezone, timedelta
import numpy as np

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

    # 画像の上10%、右60% でカット（日付のところだけ）
    img = src[0:int(hei * 0.1), int(wid * 0.6):wid]
    # cv2.imwrite('date_ptn2_1_date_cropped.jpg', img)

    # 拡大と白黒化
    img = grayAndResize(img)
    # cv2.imwrite('date_ptn2_2_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 11").replace(".", "").replace(",", "")
    print(txt)

    # 取得した日付が 5日前～現在 の間だったら有効とする
    JST = timezone(timedelta(hours=+9), 'JST')
    rangeEnd = datetime.now(JST)
    rangeStart = rangeEnd - datetime.timedelta(days=5)

    # 年月日時を抽出1
    dt_match = re.search("(\d{4}).*年(\d{1,2}).*月(\d{1,2}).*日(\d{1,2}).*", txt)    
    print(dt_match)
    if dt_match is not None and len(dt_match.groups()) == 4:
        y, m, d, h = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, h, tzinfo=JST)
        print(dt_update)
        if (rangeStart < dt_update) & (dt_update < rangeEnd):
            return dt_update.strftime("%Y/%m/%d %H:00")

    # 年月日時を抽出2
    dt_match = re.search("(\d{4}).*?(\d{1,2}).*?(\d{1,2}).*?(\d{1,2}).*", txt)    
    print(dt_match.groups())
    if dt_match is not None and len(dt_match.groups()) == 4:
        y, m, d, h = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, h, tzinfo=JST)
        print(dt_update)
        if (rangeStart < dt_update) & (dt_update < rangeEnd):
            return dt_update.strftime("%Y/%m/%d %H:00")

    # 年月日だけでも抽出
    dt_match = re.search("(\d{4}).*年(\d{1,2}).*月(\d{1,2}).*", txt)
    print(txt)
    if dt_match is not None and len(dt_match.groups()) == 3:
        y, m, d = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, 0, tzinfo=JST)
        print(dt_update)
        if (rangeStart < dt_update) & (dt_update < rangeEnd):
            return dt_update.strftime("%Y/%m/%d %0:00")

    raise ValueError("OCR Failed. 更新日が取得できませんでした。")
