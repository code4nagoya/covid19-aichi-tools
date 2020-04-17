import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
from datetime import timedelta
import json
import codecs
import traceback

base_url = "https://www.pref.aichi.jp"

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)

def findpath(url):
    page_url = base_url + url
    raw_html = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(raw_html, "html.parser")
    for aa in soup.find_all("a"):
        link = aa.get("href")
        name = aa.get_text()
        if "県内発生事例一覧" in name:
            table_link = link
            break
    return table_link

def convert_table(FILE_PATH):
    # 最新版のExcelをダウンロード
    page_url = base_url + FILE_PATH
    xlsx_path = "./data/source.xlsx"
    with urllib.request.urlopen(page_url) as b:
        with open(xlsx_path, "bw") as f:
            f.write(b.read())

    df = pd.read_excel(xlsx_path, header=2, index_col=None, dtype={2: object})
    df["発表日"] = df["発表日"].apply(exceltime2datetime)
    df = df.replace(0,"")
    df = add_date(df).fillna("")
    str_index = pd.Index([str(num) for num in list(df.index)])
    df = df.set_index(str_index)
    # print(df)
    # exit()

    return df

def add_date(df):
    basedate = df["発表日"]
    df["発表日"] = basedate.dt.strftime("%Y/%m/%d %H:%M")
    df["date"] = basedate.dt.strftime("%Y-%m-%d")
    df["w"] = [str(int(w)+1) if int(w)+1 != 7 else "0"
               for w in basedate.dt.dayofweek]
    df["short_date"] = basedate.dt.strftime("%m\\/%d")
    return df

def exceltime2datetime(et):
    if et < 60:
        days = pd.to_timedelta(et - 1, unit='days')
    else:
        days = pd.to_timedelta(et - 2, unit='days')
    return pd.to_datetime('1900/1/1') + days

if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    try:
        df = convert_table(FILE_PATH)
        df.to_csv('data/patients.csv', index=False, header=True)
        # convert_json(df)
    except Exception:
        print("===================")
        traceback.print_exc()
        print("===================")
