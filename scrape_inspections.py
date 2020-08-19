import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
import traceback

base_url = "https://www.pref.aichi.jp"

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)

def convert_table(url):
    dfs = pd.read_html(url, match='検査日')
    df = dfs[0]
    
    # 集計行削除
    df.drop(df.tail(1).index,inplace=True)
    
    # X月X日（X曜日）の行だけを抽出（月と週の行を除外）
    df = df.query('検査日.str.match(".*月.*日.*曜日）")', engine='python')
    
    # 属性調整
    df["備考"] = df["検査日"]
    df["合算"] = df["備考"].apply(is_total)
    df["検査日"] = df["検査日"].apply(chg_date)
    # print(df)
    # exit()

    return df

def chg_date(str_date):
    y = datetime.now().year
    if '～' in str_date:
        match = re.search('～.*', str_date)
        str_date = match.group(0)

    m, d = map(int, re.findall("[0-9]{1,2}", str_date))
    return pd.Timestamp(year=y, month=m, day=d).strftime("%Y/%m/%d")

def is_total(d):
    result = ''
    if '～' in d:
        result = '○'
    return result

if __name__ == "__main__":
    url = "/site/covid19-aichi/kansensya-kensa.html"
    page_url = base_url + url
    try:
        df = convert_table(page_url)
        df.to_csv('data/inspections_summary.csv', index=False, header=True)

    except Exception:
        print("===================")
        traceback.print_exc()
        print("===================")
    
