'''
このコードはimabariさんのコードを元に作成しています。

https://github.com/imabari/covid19-data/blob/master/aichi/aichi_ocr.ipynb
'''

import pathlib
import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from PIL import Image
except ImportError:
    import Image
    
import pytesseract
import cv2
import datetime
import csv

def get_file(url, dir="."):

    r = requests.get(url)

    p = pathlib.Path(dir, "main_summary" + pathlib.PurePath(url).suffix)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open(mode='wb') as fw:
        fw.write(r.content)

    return p

def recognition(jpg_path):
    src = cv2.imread(str(jpg_path))
    img = cv2.inRange(src, (150, 150, 100), (255, 255, 255))

    # 範囲指定
    img_crop = img[0:550]
    txt = pytesseract.image_to_string(img_crop, lang="jpn", config="--psm 6").replace(".", "")
    print(txt)

    dt_match = re.search("(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})時", txt)    
    y, m, d, h = map(int, dt_match.groups())
    dt_update = datetime.datetime(y, m, d, h).strftime("%Y/%m/%d %H:00")

    # ※1 ※2 または (注) で始まる文を抽出
    remarks = re.findall("^(※. .*|\(注\) .*)$", txt, re.M)
    # 行頭の ※1 ※2 や (注) を削除（空白以降を抽出）
    remarks = list(map(lambda word:word[word.find(' ')+1:], remarks))

    # xx人 な箇所を全て抜き出す
    data = list(map(lambda str:str.replace('人', ''), re.findall("[0-9]+人", txt))) 
    # dataの先頭から [検査実施人数,陽性患者数,入院,軽症無症状,中等症,重症,入院調整,施設入所,自宅療養,調整,退院,死亡] であると決め打ち
    data = data[0:12]

    return [dt_update, data, remarks]

def to_csv(dt, row, remarks, dir):
    p = pathlib.Path(dir, 'main_summary_recognized.csv')

    with p.open(mode='w') as fw:
        writer = csv.writer(fw)
        writer.writerow(["更新日時","検査実施人数","陽性患者数","入院","軽症無症状","中等症","重症","入院調整","施設入所","自宅療養","調整","退院","死亡","入院中","軽症中等症","転院","備考"])
        writer.writerow([dt] + row + ["", "", ""] + ["".join(remarks)])

if __name__ == "__main__":
    url = "https://www.pref.aichi.jp/site/covid19-aichi/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    }
    r = requests.get(url, headers=headers)

    r.raise_for_status()

    soup = BeautifulSoup(r.content, "html5lib")
    src = soup.find("img", alt=re.compile("検査陽性者$")).get("src")
    link = urljoin(url, src)
    jpg_path = get_file(link, "./data")
    res = recognition(jpg_path)
    print(res[0])
    print(res[1])
    print(res[2])

    to_csv(res[0], res[1], res[2], "./data")
