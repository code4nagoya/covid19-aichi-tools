# covid19-aichi-tools

[愛知県 新型コロナウイルス感染症対策サイト](https://stopcovid19.code4.nagoya)用のデータ更新用スクリプト

## 必要なもの

* Python3

## 準備

下記の2ファイルを更新する。

* data/patients.csv
  * 出典元: https://www.pref.aichi.jp/site/covid19-aichi/kansensya-kensa.html の県内発生事例一覧(PDFファイル)
* data/main_summary.csv
  * 出典元: https://www.pref.aichi.jp/site/covid19-aichi/ の検査陽性者の状況

## 使い方


```
$ git clone https://github.com/hajime-miyauchi/covid19-aichi-tools.git
$ cd covid19-aichi-tools
$ python3 build_json.py | python3 pretty_json.py > data/data.json
```

生成されたdata/data.jsonを、下記リポジトリのdata/data.jsonと差し替える。

https://github.com/code4nagoya/covid19

