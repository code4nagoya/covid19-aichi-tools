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
import os
import csv
import pandas as pd

if __name__ == "__main__":

    dt_col = "更新日時"
    date_col = "更新日"

    # 更新日時列 → 更新日列 の生成
    def update_at_ymd(x):
        hit = x[dt_col].find(' ')
        if hit < 0:
            return x[dt_col]
        return x[dt_col][:hit]

    # 前回CSV読み込み
    df_master = pd.read_csv("./data/main_summary_history_master.csv", dtype=str)
    df_master[date_col] = df_master.apply(update_at_ymd, axis=1) # 更新日列追加
    
    # OCR結果CSV読み込み
    ocr_path = "./data/main_summary_recognized.csv"
    if os.path.isfile(ocr_path):
        df_recog = pd.read_csv(ocr_path, dtype=str)
        df_recog[date_col] = df_recog.apply(update_at_ymd, axis=1) # 更新日列追加

        # 前回CSVとOCR結果CSVをマージ(同一更新日はOCR結果CSVを採用)
        df_merged = df_recog.set_index(date_col).combine_first(df_master.set_index(date_col))
        df_merged[date_col] = df_merged.apply(update_at_ymd, axis=1) # 更新日列追加
        print("Merged main_summary_history_master.csv to main_summary_recognized.csv")

    else:
        print("main_summary_recognized.csv not found, skipped.")
        df_merged = df_master

    # GoogleスプレッドシートCSV読み込み
    df_sheet = pd.read_csv("./data/main_summary_history_sheet.csv", dtype=str)
    df_sheet[date_col] = df_sheet.apply(update_at_ymd, axis=1) # 更新日列追加

    # さらにGoogleスプレッドシートCSVをマージ(同一更新日はGoogleスプレッドシートCSVを採用)
    df_csv = df_sheet.set_index(date_col).combine_first(df_merged.set_index(date_col))
    print("Merged to main_summary_history_sheet.csv")

    # 更新日時の昇順で並び替えてCSV出力
    df_csv = df_csv.sort_values(by=[dt_col], ascending=True)
    # df_csv = df_csv.astype(str)
    order = ["更新日時","検査実施人数","陽性患者数","入院","軽症無症状","中等症","重症","入院調整","施設入所","自宅療養","調整","退院","死亡","入院中","軽症中等症","転院","備考"]
    df_csv[order].to_csv("./data/main_summary_history.csv", index=False, header=True)
    print("Wrote to main_summary_history.csv")
