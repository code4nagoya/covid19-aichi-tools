'''
「検査陽性者の状況」画像から更新日を抽出する処理 パターン１
'''
import re
import pytesseract
import cv2
import datetime

def recognize(jpg_path):
    src = cv2.imread(str(jpg_path))
    hei = src.shape[0]
    wid = src.shape[1]

    # 画像の上10%、右60% でカット（日付のところだけ）
    src = src[0:int(hei * 0.1), int(wid * 0.6):wid]
    # cv2.imwrite('date_ptn1_1_date_cropped.jpg', src)

    # 拡大と白黒化
    height = src.shape[0]
    width = src.shape[1]
    tmp = cv2.resize(src, (int(width * 2), int(height * 2)))
    img = cv2.inRange(tmp, (145, 125, 110), (255, 255, 255))
    # cv2.imwrite('date_ptn1_2_resized.jpg', img)

    # 範囲指定
    # ref http://blog.machine-powers.net/2018/08/02/learning-tesseract-command-utility/
    txt = pytesseract.image_to_string(img, lang="jpn", config="--psm 11").replace(".", "").replace(",", "")
    print(txt)

    # 年月日時を抽出1
    dt_match = re.search("(\d{4}).*年(\d{1,2}).*月(\d{1,2}).*日(\d{1,2}).*", txt)    
    print(dt_match)
    if dt_match is not None and len(dt_match.groups()) == 4:
        y, m, d, h = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, h).strftime("%Y/%m/%d %H:00")
        print(dt_update)
        return dt_update

    # 年月日時を抽出2
    dt_match = re.search("(\d{4}).*?(\d{1,2}).*?(\d{1,2}).*?(\d{1,2}).*", txt)    
    print(dt_match.groups())
    if dt_match is not None and len(dt_match.groups()) == 4:
        y, m, d, h = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, h).strftime("%Y/%m/%d %H:00")
        print(dt_update)
        return dt_update

    # 年月日だけでも抽出
    dt_match = re.search("(\d{4}).*年(\d{1,2}).*月(\d{1,2}).*", txt)
    print(txt)
    if dt_match is not None and len(dt_match.groups()) == 3:
        y, m, d = map(int, dt_match.groups())
        dt_update = datetime.datetime(y, m, d, 0).strftime("%Y/%m/%d %0:00")
        print(dt_update)
        return dt_update

    raise ValueError("OCR Failed. 更新日が取得できませんでした。")
