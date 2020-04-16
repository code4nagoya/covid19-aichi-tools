import csv
import io
import json
import pandas as pd
import sys
from dateutil import tz
from datetime import datetime, date, time, timedelta

# Japan Standard Time (UTC + 09:00)
JST = tz.gettz('Asia/Tokyo')
JST_current_time = datetime.now(tz=JST).strftime('%Y/%m/%d %H:%M')


patients_list = []
patients_summary_dic = {}
main_summary_dic = {}

# 引数を取得 異常系処理はしてないので注意
args = sys.argv

with open('data/patients.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        patients_list.append(row)
        patients_summary_dic.setdefault(row['date'], 0)
        patients_summary_dic[row['date']] += 1

# 日付のリストを生成
strdt = datetime.strptime("2020-01-26", '%Y-%m-%d')  # 開始日
enddt = datetime.strptime(args[1], '%Y-%m-%d')  # 終了日

# 日付差の日数を算出（リストに最終日も含めたいので、＋１しています）
days_num = (enddt - strdt).days + 1

datelist = []
for i in range(days_num):
    datelist.append(strdt + timedelta(days = i))

patients_summary_list = []

for date in datelist:
    patients_summary_dic.setdefault(date.strftime('%Y-%m-%d'), 0)
    patients_summary_list.append({
        "日付": date.strftime('%Y-%m-%d'),
        "小計": patients_summary_dic[date.strftime('%Y-%m-%d')]
    })

main_summary_dic = {}

with open('data/main_summary.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        main_summary_dic[row[0]] = int(row[1])

# main_summary_history.csvをPandasのDataframeに変換
main_summary_history_df = pd.read_csv('data/main_summary_history.csv', keep_default_na=False)

# 検査件数の読み込み
inspections_summary_list = []
with open('data/inspections_summary.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        inspections_summary_list.append({
            "日付": datetime.strptime(row['検査日'], '%Y/%m/%d').strftime('%Y-%m-%d'),
            "小計": int(row['検査件数（件）']),
            "合算": row['合算']
        })

data = {
    "patients": {
        "date": JST_current_time,
        "data": patients_list
    },
    "patients_summary" : {
        "date": JST_current_time,
        "data": patients_summary_list
    },
    "inspections_summary" : {
        "date": JST_current_time,
        "data": inspections_summary_list
    },
    "lastUpdate": JST_current_time,
    "main_summary" : {
            "attr": "検査実施人数",
            "value": main_summary_dic['検査実施人数'],
            "children": [
                {
                    "attr": "陽性患者数",
                    "value": main_summary_dic['陽性患者数'],
                    "children": [
                        {
                            "attr": "入院中",
                            "value": main_summary_dic['入院中'],
                            "children": [
                                {
                                    "attr": "軽症・中等症",
                                    "value": main_summary_dic['軽症・中等症']
                                },
                                {
                                    "attr": "重症",
                                    "value": main_summary_dic['重症']
                                }
                            ]
                        },
                        {
                            "attr": "退院",
                            "value": main_summary_dic['退院']
                        },
                        {
                            "attr": "転院",
                            "value": main_summary_dic['転院']
                        },
                        {
                            "attr": "死亡",
                            "value": main_summary_dic['死亡']
                        }
                    ]
                }
            ]
    },
    "main_summary_history": {
        "date": JST_current_time,
        "data": json.loads(main_summary_history_df.to_json(orient='records', force_ascii=False))
    }
}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print(json.dumps(data, indent=4, ensure_ascii=False))
