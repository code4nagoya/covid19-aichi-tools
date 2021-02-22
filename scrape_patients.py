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

import pandas as pd
from bs4 import BeautifulSoup
import os
import re
import traceback

import pathlib
import requests
import pdfplumber

base_url = "https://www.pref.aichi.jp"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
}

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)

def findpath(url, searchWord):
    page_url = base_url + url
    r = requests.get(page_url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, "html.parser")    

    # ↓のような HTML を想定
    # <p>
    #   <span>▶ 愛知県内の発生事例</span>
    #   <a href="/uploaded/attachment/359857.pdf">12月</a>
    #   <a href="/uploaded/attachment/354550.pdf">11月まで</a>
    # </p>
    patientBlock = soup.find(text=lambda t: t and t.find("発生事例") >= 0).parent.parent
    table_link = ""
    ext = ""
    for aa in patientBlock.find_all("a"):
        link = aa.get("href")
        name = aa.get_text()
        if searchWord in name:
            table_link = link
            if "PDFファイル" in name:
                ext = "pdf"
    return table_link, ext

def fetch_file(url, dir="."):

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    p = pathlib.Path(dir, pathlib.PurePath(url).name)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open(mode="wb") as fw:
        fw.write(r.content)
    return p

def days2date(s):

    # No.16577以降は2021年
    # TODO Noが変わる可能性があるので決め打ちはやめたい。"1月" に変化する度に year を加算する？
    y = 2021 if s.name > 16576 else 2020

    days = re.findall("[0-9]{1,2}", s["発表日"])

    if len(days) == 2:
        m, d = map(int, days)
        return pd.Timestamp(year=y, month=m, day=d)
    else:
        return pd.NaT

def convert_pdf(FILE_PATHs):
    dfs = []
    for FILE_PATH in FILE_PATHs:
        # 最新版のPDFをダウンロード
        page_url = base_url + FILE_PATH

        path_pdf = fetch_file(page_url, './data')

        with pdfplumber.open(path_pdf) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                df_tmp = pd.DataFrame(table[1:], columns=table[0])
                dfs.append(df_tmp)

    df = pd.concat(dfs).set_index("No")

    # 発表日が欠損を削除
    df.dropna(subset=["発表日"], inplace=True)
    # 欠番の行を削除
    df = df[~df["発表日"].str.contains("欠番")]

    # Noを数値に変換
    df.index = df.index.astype(int)

    # Noでソート
    df.sort_index(inplace=True)

    # 月日から年月日に変換
    df["date"] = df.apply(days2date, axis=1)
    df["発表日"] = df["date"].apply(lambda s: s.strftime("%Y/%m/%d %H:%M"))

    # 年代(age)と性別(sex)列を追加
    df["年代・性別"] = df["年代・性別"].str.normalize("NFKC")
    df_ages = df["年代・性別"].str.extract("(.+)(男性|女性|その他)").rename(columns={0: "age", 1: "sex"})
    df = df.join(df_ages)
    df["age"] = df["age"].str.strip()
    df["age"] = df["age"].replace("10歳未満代", "10歳未満")
    df["sex"] = df["sex"].str.strip()

    # CJK部首置換
    cjk = str.maketrans("⻲⻑黑戶⻯⻄⻘⻤⼾⾧⼿", "亀長黒戸竜西青鬼戸長手")
    df["住居地"] = df["住居地"].str.normalize("NFKC")
    df["住居地"] = df["住居地"].apply(lambda s: s.translate(cjk))

    p = pathlib.Path("./data/patients.csv")
    p.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(p, encoding="utf_8")

    return df

if __name__ == "__main__":

    monthYears = [
        "12月",
        "１２月",
        "1月",
        "１月",
        "2月",
        "２月",
    ]

    paths = []
    for month in monthYears:
        path, ext = findpath("/site/covid19-aichi/", month)
        
        if ext == "pdf":
            print(month + " ---> FOUND!")
            paths.append(path)
        else:
            print(month + " ---> not found.")
            continue

    if len(paths) == 0:
        print("No patients pdf.")
        exit()

    try:
        convert_pdf(paths)
    except Exception:
        print("===================")
        traceback.print_exc()
        print("===================")
