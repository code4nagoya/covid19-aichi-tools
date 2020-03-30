import csv
import json
from datetime import datetime, date, time, timedelta
import io, sys

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
        "date": datetime.now().strftime('%Y/%m/%d %H:%M'),
        "data": inspections_summary_list
    }
}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print(json.dumps(data, indent=4, ensure_ascii=False))
