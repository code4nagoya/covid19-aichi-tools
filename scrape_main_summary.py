'''
このコードはimabariさんのコードを元に作成しています。

https://github.com/imabari/covid19-data/blob/master/aichi/aichi_ocr.ipynb
'''

import pathlib
import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import pytesseract
import cv2
import datetime
import csv

import recognize_main_summary_date_1 as date_pattern1
import recognize_main_summary_date_2 as date_pattern2
import recognize_main_summary_table_1 as table_pattern1
import recognize_main_summary_table_2 as table_pattern2
import recognize_main_summary_table_3 as table_pattern3
import recognize_main_summary_remarks_1 as remarks_pattern1
import recognize_main_summary_remarks_2 as remarks_pattern2

def get_file(url, dir="."):

    r = requests.get(url)

    p = pathlib.Path(dir, "main_summary" + pathlib.PurePath(url).suffix)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open(mode='wb') as fw:
        fw.write(r.content)

    return p

def recognize_date_patterns(reconize_funcs):
    pattern = 0
    for reconize_date in reconize_funcs:
        try:
            pattern = pattern + 1
            print("Pattern" + str(pattern) + " Start")
            data = reconize_date(jpg_path)

            return pattern, data

        except Exception as e:
            print(e)

    return None

def recognize_remarks_patterns(reconize_funcs):
    pattern = 0
    for reconize_remarks in reconize_funcs:
        try:
            pattern = pattern + 1
            print("Pattern" + str(pattern) + " Start")
            data = reconize_remarks(jpg_path)

            # Validation
            if len(data) <= 0:
                raise ValueError("OCR Failed. 注記が取得できませんでした。")

            return pattern, data

        except Exception as e:
            print(e)

    return None

def recognize_table_patterns(reconize_funcs):
    pattern = 0
    for reconize_table in reconize_funcs:
        try:
            pattern = pattern + 1
            print("Pattern" + str(pattern) + " Start")
            row = reconize_table(jpg_path)

            # dataの先頭から [検査実施人数,陽性患者数,入院,入院_軽症無症状,中等症,重症,入院調整,施設入所,自宅療養,調整,退院,死亡] であると決め打ち
            data = row[0:12]

            # Valiadation
            # 入院者数の合計列と要素列群値の合計が一致するか？
            if data[2] != sum(i for i in data[3:6]):
                raise ValueError("OCR Failed. 入院者数が一致しませんでした。")
            # 陽性者数の合計列と要素列群値の合計が一致するか？
            if data[1] != sum(i for i in data[3:]):
                raise ValueError("OCR Failed. 陽性者数が一致しませんでした。")

            return pattern, data

        except Exception as e:
            print(e)

    return None

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
    # jpg_path = "./data/main_summary0826.jpg"

    print("更新日を抽出")
    hit_date_pattern, date = recognize_date_patterns([
        (lambda path: date_pattern1.recognize(path)),
        (lambda path: date_pattern2.recognize(path)),
    ])

    if date is None:
        raise ValueError("OCR Failed. 更新日を抽出できませんでした。")
    print("更新日を抽出 -> Pattern" + str(hit_date_pattern) + "で成功")


    print("数値データを抽出")
    hit_table_pattern, nums = recognize_table_patterns([
        (lambda path: table_pattern1.recognize(path)),
        (lambda path: table_pattern2.recognize(path)),
        (lambda path: table_pattern3.recognize(path)),
    ])

    if nums is None:
        raise ValueError("OCR Failed. 表から数値データを抽出できませんでした。")
    print("数値データを抽出 -> Pattern" + str(hit_table_pattern) + "で成功")


    print("注記データを抽出")
    hit_remarks_pattern, remarks = recognize_remarks_patterns([
        (lambda path: remarks_pattern2.recognize(path)),
        # (lambda path: remarks_pattern1.recognize(path)),
    ])

    if remarks is None:
        raise ValueError("OCR Failed. 注記データを抽出できませんでした。")
    print("注記データを抽出 -> Pattern" + str(hit_remarks_pattern) + "で成功")


    print("更新日時", date)
    print("数値群", nums)
    print("注記", remarks)
    to_csv(date, nums, remarks, "./data")
    print("Wrote to main_summary_recognized.csv")
