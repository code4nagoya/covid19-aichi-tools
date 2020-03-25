# covid19-aichi-tools

[愛知県 新型コロナウイルス感染症対策サイト](https://stopcovid19.code4.nagoya)用のデータ更新用スクリプト

## 必要なもの

* Python3

## 準備

リポジトリをクローンする。

```
$ git clone https://github.com/hajime-miyauchi/covid19-aichi-tools.git
$ cd covid19-aichi-tools
```

下記の2ファイルを更新する。

* data/patients.csv
* data/main_summary.csv

Googleドライブで管理している最新データをダウンロードする場合は下記コマンドを実行する。

```
$ wget "https://docs.google.com/spreadsheets/d/12qStuXjsI8GE8qI1mLPLV--6TQcxAMPDu3-k9RCHN1k/export?format=csv&gid=0" -O data/patients.csv
$ wget "https://docs.google.com/spreadsheets/d/1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/export?format=csv&gid=0" -O data/main_summary.csv
```

## 使い方

https://www.pref.aichi.jp/site/covid19-aichi/

愛知県新型コロナウイルス感染症トップページの愛知県の感染症発生状況（画像）に記載のある日付を
YYYY-MM-DD形式で引数に付けてコマンドを実行してください。

3月25日○○時現在であれば

```
$ python3 build_json.py　2020-03-25 > data/data.json
```

生成されたdata/data.jsonを、下記リポジトリのdata/data.jsonと差し替える。

https://github.com/code4nagoya/covid19

## データの形式について

### data/patients.csv

「陽性患者数」や「陽性患者の属性」のグラフに使用するデータです。

出典元: https://www.pref.aichi.jp/site/covid19-aichi/kansensya-kensa.html の県内発生事例一覧(PDFファイル)

* 下記のヘッダ行が必要です。
* ヘッダ行の各カラム名がそのままJSONに出力されます。

| ヘッダ | データ | 例 |
| --- | --- | --- |
| No | 連番の数値 | 1 | 
| 発表日 | YYYY/m/d | 2020/2/24 |
| 年代・性別 | 文字列 | 40代男性 | 
| 国籍 | 文字列 | 日本 |
| 住居地 | 文字列 | 名古屋市 |
| 接触状況 | 文字列 | No.4と接触 |
| 備考 | 文字列 | 本県発表 |
| date | YYYY-MM-DD | 2020-02-24 |
| w | 曜日を表す数値(0が日曜日) | 2 |
| short_date | YY/MM | 02¥/24 |

### data/main_summary.csv

「検査陽性者の状況」のグラフに使用するデータです。

出典元: https://www.pref.aichi.jp/site/covid19-aichi/ の検査陽性者の状況

* ヘッダ行は不要です。
* ヘッダ列が必要です。
* 下記の行が必要です。

| ヘッダ列(1列目) | データ列(2列目) |
| --- | --- |
| 検査実施人数 | 数値 | 
| 陽性患者数 | 数値 |
| 入院中 | 数値 |
| 軽症・中等症 | 数値 |
| 重症 | 数値 |
| 退院 | 数値 | 
| 転院 | 数値 |
| 死亡 | 数値 | 

