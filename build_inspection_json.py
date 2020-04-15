import csv
import io
import json
import sys
from dateutil import tz
from datetime import datetime, date, time, timedelta

# Japan Standard Time (UTC + 09:00)
JST = tz.gettz('Asia/Tokyo')
JST_current_time = datetime.now(tz=JST).strftime('%Y/%m/%d %H:%M')

# 検査件数の読み込み
inspections_summary_list = []
with open('data/inspections_summary.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        inspections_summary_list.append({
            "日付": datetime.strptime(row['検査日'], '%Y/%m/%d').strftime('%Y-%m-%d'),
            "小計": int(row['検査件数（件）'])
        })

data = {
    "inspections_summary" : {
        "date": JST_current_time,
        "data": inspections_summary_list
    }
}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print(json.dumps(data, indent=2, ensure_ascii=False))
