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
patients_date_num_dic = {}
patients_date_place_dic = {}
patients_date_age_sex_dic = {}
patients_date_sex_dic = {}

# 引数を取得 異常系処理はしてないので注意
args = sys.argv

with open('data/patients.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        patients_list.append(row)
        dt = row['date']
        patients_date_num_dic.setdefault(dt, 0)
        patients_date_num_dic[dt] += 1

        patients_date_place_dic.setdefault(dt, {})
        placeDic = patients_date_place_dic[dt]
        placeDic.setdefault(row['住居地'], 0)
        placeDic[row['住居地']] += 1

        sex = row['年代・性別'][-2:]
        age = row['年代・性別'].replace(sex, '')
        patients_date_age_sex_dic.setdefault(dt, {})
        ageDic = patients_date_age_sex_dic[dt]
        ageDic.setdefault(age, {})
        sexDic = ageDic[age]
        sexDic.setdefault(sex, 0)
        sexDic[sex] += 1


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
    dtKey = date.strftime('%Y-%m-%d')
    if (not (dtKey in patients_date_num_dic)) and foundZero:
        continue
    else:
        foundZero = False
        patients_date_num_dic.setdefault(dtKey, 0)
        patients_date_place_dic.setdefault(dtKey, {})
        patients_date_age_sex_dic.setdefault(dtKey, {})
        patients_date_sex_dic.setdefault(dtKey, {})
        patients_summary_list.append({
            "日付": dtKey,
            "小計": patients_date_num_dic[dtKey],
            "住居地": patients_date_place_dic[dtKey],
            "年代": patients_date_age_sex_dic[dtKey],
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
            "小計": int(row['PCR検査件数（件）']),
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
