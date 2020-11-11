'''
このコードはKMiura.ioさんのコードを元に作成しています。

https://github.com/code4nagoya/covid19-scrape

MIT License

Copyright (c) 2020 KMiura.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import camelot
import codecs
import json
import os
import pandas as pd
import re
import traceback
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime


base_url = "https://www.pref.aichi.jp"

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)

def findpath(url, searchWord):
    page_url = base_url + url
    raw_html = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(raw_html, "html.parser")
    for aa in soup.find_all("a"):
        link = aa.get("href")
        name = aa.get_text()
        if searchWord in name:
            table_link = link
            if "Excelファイル" in name:
                ext = "xlsx"
                # Excelファイルなら確定
                break
            elif "PDFファイル" in name:
                ext = "pdf"
    return table_link, ext

def convert_pdf(FILE_PATH, pdf_path, csv_path):
    # 最新版のPDFをダウンロード
    page_url = base_url + FILE_PATH
    with urllib.request.urlopen(page_url) as b:
        with open(pdf_path, "bw") as f:
            f.write(b.read())

    tables = camelot.read_pdf(
        pdf_path, pages="1-end", split_text=True,
        strip_text="\n", line_scale=40)

    df_csv = pd.concat([table.df for table in tables])

    # 2行目以降の(各頁に挿入される)ヘッダ行を除去
    df_csv_header = df_csv[:1]
    df_csv_body = df_csv[1:]
    df_csv_body = df_csv_body[df_csv_body[0].str.isnumeric()] # No列が数値の行を抽出
    df_csv_body = df_csv_body[df_csv_body[1].str.match(".*月.*日")] # 発表日列が○月○日を行を抽出(欠番を除去)
    df_csv = pd.concat([df_csv_header, df_csv_body])
    
    # csvに保存
    df_csv.to_csv(csv_path, index=False, header=False)
    df = pd.read_csv(csv_path, parse_dates=["発表日"], date_parser=my_parser)
    df = add_date(df).fillna("")
    str_index = pd.Index([str(num) for num in list(df.index)])
    df = df.set_index(str_index)
    # df.index.name = "No"
    # print(df)
    return df

def convert_xlsx(FILE_PATH, xlsx_path):
    # 最新版のExcelをダウンロード
    page_url = base_url + FILE_PATH
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

def my_parser(s):
    y = datetime.now().year
    m, d = map(int, re.findall("[0-9]{1,2}", s))
    return pd.Timestamp(year=y, month=m, day=d)

def exceltime2datetime(et):
    if et < 60:
        days = pd.to_timedelta(et - 1, unit='days')
    else:
        days = pd.to_timedelta(et - 2, unit='days')
    return pd.to_datetime('1900/1/1') + days

if __name__ == "__main__":

    months = ["8月", "9月", "10月", "11月", "12月"]

    i = 0
    dfs = []
    for month in months:
        try:
            i = i + 1
            path, ext = findpath("/site/covid19-aichi/", month)
            
            if ext == "xlsx":
                df = convert_xlsx(path, "./data/source" + str(i) + "." + ext)
            elif ext == "pdf":
                df = convert_pdf(path, "./data/source" + str(i) + "." + ext, "./data/source" + str(i) + ".csv")
            else:
                continue

            dfs.append(df)

        except Exception:
            print(month + " is not found.")
            continue

    if len(dfs) == 0:
        print("No patients pdf/xlsx.")
        exit()

    try:
        df = pd.concat(dfs)
        df.to_csv('data/patients.csv', index=False, header=True)
    except Exception:
        print("===================")
        traceback.print_exc()
        print("===================")
