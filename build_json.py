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

# 引数を取得 異常系処理はしてないので注意
args = sys.argv

# 市町村名と市区町コード
cities = {
    '名古屋市':'23100',
    '豊橋市':'23201',
    '岡崎市':'23202',
    '一宮市':'23203',
    '瀬戸市':'23204',
    '半田市':'23205',
    '春日井市':'23206',
    '豊川市':'23207',
    '津島市':'23208',
    '碧南市':'23209',
    '刈谷市':'23210',
    '豊田市':'23211',
    '安城市':'23212',
    '西尾市':'23213',
    '蒲郡市':'23214',
    '犬山市':'23215',
    '常滑市':'23216',
    '江南市':'23217',
    '小牧市':'23219',
    '稲沢市':'23220',
    '新城市':'23221',
    '東海市':'23222',
    '大府市':'23223',
    '知多市':'23224',
    '知立市':'23225',
    '尾張旭市':'23226',
    '高浜市':'23227',
    '岩倉市':'23228',
    '豊明市':'23229',
    '日進市':'23230',
    '田原市':'23231',
    '愛西市':'23232',
    '清須市':'23233',
    '北名古屋市':'23234',
    '弥富市':'23235',
    'みよし市':'23236',
    'あま市':'23237',
    '長久手市':'23238',
    '東郷町':'23302',
    '豊山町':'23342',
    '大口町':'23361',
    '扶桑町':'23362',
    '大治町':'23424',
    '蟹江町':'23425',
    '飛島村':'23427',
    '阿久比町':'23441',
    '東浦町':'23442',
    '南知多町':'23445',
    '美浜町':'23446',
    '武豊町':'23447',
    '幸田町':'23501',
    '設楽町':'23561',
    '東栄町':'23562',
    '豊根村':'23563',
}

# 性別
sexes = {
    '男性':'男性',
    '女性':'女性',
}

# 年代
ages = {
    '10歳未満':'10歳未満',
    '10代':'10代',
    '20代':'20代',
    '30代':'30代',
    '40代':'40代',
    '50代':'50代',
    '60代':'60代',
    '70代':'70代',
    '80代':'80代',
    '90代':'90代',
    '100代':'100代',
    '110代':'110代',
}

with open('data/patients.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        patients_list.append(row)
        dt = row['date']
        patients_date_num_dic.setdefault(dt, 0)
        patients_date_num_dic[dt] += 1

        patients_date_place_dic.setdefault(dt, {})
        placeDic = patients_date_place_dic[dt]
        cityCode = cities.get(row['住居地'], 'NOT_FOUND')
        placeDic.setdefault(cityCode, 0)
        placeDic[cityCode] += 1

        sex = sexes.get(row['sex'], 'その他')
        age = ages.get(row['age'], 'その他')
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
