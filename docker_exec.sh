#!/bin/bash

echo 1.検査陽性者の状況 start
# wget "https://raw.githubusercontent.com/code4nagoya/covid19/master/data/main_summary_history.csv" -O /covid19/data/main_summary_history_master.csv
# wget "https://docs.google.com/spreadsheets/d/1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/export?format=csv&gid=1019512361" -O /covid19/data/main_summary_history_sheet.csv
python3 /covid19/scrape_main_summary2.py #愛知県HPからOCR
python3 /covid19/merge_main_summary.py #CSV群を main_summary_history.csv にマージ
# cp /covid19/data/main_summary_history_sheet.csv /covid19/data/main_summary_history.csv
echo 1.検査陽性者の状況 end

# echo 2.愛知県内発生事例（感染者一覧） start
# # wget "https://docs.google.com/spreadsheets/d/12qStuXjsI8GE8qI1mLPLV--6TQcxAMPDu3-k9RCHN1k/export?format=csv&gid=0" -O /covid19/data/patients.csv
# python3 /covid19/scrape_patients.py #愛知県HPからスクレイピング
# echo 2.愛知県内発生事例（感染者一覧） end

# echo 3.検査件数 start
# # wget "https://docs.google.com/spreadsheets/d/1ivROd_s3AmvY480XKEZR_COAlx08gOGxZYRYubxghP0/export?format=csv&gid=0" -O /covid19/data/inspections_summary.csv
# python3 /covid19/scrape_inspections.py #愛知県HPからスクレイピング
# echo 3.検査件数 end

# echo 4.検査人数 start
# wget "https://docs.google.com/spreadsheets/d/1-w8rowCmCG7lmuo5c0jQ0Dh2Frl4hOmpVrZ2IH9sPpg/export?format=csv&gid=0" -O /covid19/data/inspection_persons_summary.csv
# echo 4.検査人数 end

# echo 5.data.json 生成 start
# python3 /covid19/build_json.py `date -d "1 day ago" +'%Y-%m-%d'` > /covid19/data/data.json
# echo 5.data.json 生成 end

# # cat /covid19/data/*.json /covid19/data/*.csv
# ls /covid19/data/*.json /covid19/data/*.csv
