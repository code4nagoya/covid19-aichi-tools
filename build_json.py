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

# 日付の新しい順に辿って小計が 0 でない日から開始する
foundZero = True
for date in reversed(datelist):
    if (not (date.strftime('%Y-%m-%d') in patients_summary_dic)) and foundZero:
        continue
    else:
        foundZero = False
        patients_summary_dic.setdefault(date.strftime('%Y-%m-%d'), 0)
        patients_summary_list.append({
            "日付": date.strftime('%Y-%m-%d'),
            "小計": patients_summary_dic[date.strftime('%Y-%m-%d')]
        })

patients_summary_list = patients_summary_list[::-1] # 日付の昇順に並び替え


# main_summary_history.csvをPandasのDataframeに変換
main_summary_history_df = pd.read_csv('data/main_summary_history.csv', keep_default_na=False)

# inspection_persons_summary.csvをPandasのDataframeに変換
inspection_persons_summary_df = pd.read_csv('data/inspection_persons_summary.csv', keep_default_na=False)

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
    "lastUpdate": JST_current_time,
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
    "main_summary_history": {
        "date": JST_current_time,
        "data": json.loads(main_summary_history_df.to_json(orient='records', force_ascii=False))
    },
    "inspection_persons_summary": {
        "date": JST_current_time,
        "data": json.loads(inspection_persons_summary_df.to_json(orient='records', force_ascii=False))
    }
}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print(json.dumps(data, indent=4, ensure_ascii=False))
