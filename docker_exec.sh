#!/bin/bash

# wget "https://docs.google.com/spreadsheets/d/12qStuXjsI8GE8qI1mLPLV--6TQcxAMPDu3-k9RCHN1k/export?format=csv&gid=0" -O /covid19/data/patients.csv
wget "https://docs.google.com/spreadsheets/d/1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/export?format=csv&gid=1019512361" -O /covid19/data/main_summary_history.csv
# wget "https://docs.google.com/spreadsheets/d/1ivROd_s3AmvY480XKEZR_COAlx08gOGxZYRYubxghP0/export?format=csv&gid=0" -O /covid19/data/inspections_summary.csv

# 愛知県HPから感染者一覧を取得してスクレイピング
python3 /covid19/scrape_patients.py #PDF版
# python3 /covid19/scrape_patients_excel.py # EXCEL版

# 愛知県HPから新型コロナウイルス遺伝子検査件数を取得してスクレイピング
python3 /covid19/scrape_inspections.py

python3 /covid19/build_json.py `date -d "1 day ago" +'%Y-%m-%d'` > /covid19/data/data.json

# cat /covid19/data/*.json /covid19/data/*.csv
ls /covid19/data/*.json /covid19/data/*.csv
