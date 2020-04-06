# 愛知県新型コロナウイルス感染症ページ
# 【愛知県の感染症発生状況】の自動分析プログラム
# created by H. Sawano


import pyocr
import pyocr.builders
import cv2
from PIL import Image
import sys
import re # 正規表現
import numpy as np
import csv

def textFrom(img):
    th = 200
    ret, binary_img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)
    txt = tool.image_to_string(
        Image.fromarray(binary_img),
        lang='jpn'
    )
    cv2.imshow("roi1", binary_img)
    num = re.sub("\\D", "", txt)
    return (num)

def textFromDark(img):
    ret, binary_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    txt = tool.image_to_string(
        Image.fromarray(binary_img),
        lang='jpn'
    )
    num = re.sub("\\D", "", txt)
    return (num)


# 利用可能なOCRツールを取得
tools = pyocr.get_available_tools()

if len(tools) == 0:
    print("OCR is not found.")
    sys.exit(1)

tool = tools[0]

args = sys.argv
if len(args) < 2:
    print("Image is not input.")
    sys.exit()

# read image
src_img = cv2.imread(args[1])
if src_img is None:
    print(args[1] + " is not image file.")
    sys.exit()

gray_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)

# 検査実施人数
inspectors_img = gray_img[170:220, 23:84]
inspectors_img = cv2.resize(inspectors_img, None, fx=3, fy=3)
inspectors_txt = textFrom(inspectors_img)

# 陽性数
positive_img = gray_img[170:220, 90:145]
positive_img = cv2.resize(positive_img, None, fx=3, fy=3)
positive_txt = textFromDark(positive_img)

# 入院中
hospitalized_img = gray_img[170:220, 150:210]
hospitalized_img = cv2.resize(hospitalized_img, None, fx=3, fy=3)
hospitalized_txt = textFromDark(hospitalized_img)

# 軽症・中等症
mild_moderate_img = gray_img[170:220, 220:270]
mild_moderate_img = cv2.resize(mild_moderate_img, None, fx=2, fy=2)
mild_moderate_txt = textFrom(mild_moderate_img)

# 重症
severe_img = gray_img[170:220, 280:330]
severe_img = cv2.resize(severe_img, None, fx=3, fy=3)
severe_txt = textFrom(severe_img)

# 退院
discharge_img = gray_img[170:220, 340:390]
discharge_img = cv2.resize(discharge_img, None, fx=3, fy=3)
discharge_txt = textFrom(discharge_img)

# 転院
transfer_img = gray_img[170:220, 400:450]
transfer_img = cv2.resize(transfer_img, None, fx=3, fy=3)
transfer_txt = textFrom(transfer_img)

# 死亡
death_img = gray_img[180:210, 480:540]
death_img = cv2.resize(death_img, None, fx=3, fy=3)
kernel = np.ones((5,5),np.uint8)
death_img = cv2.dilate(death_img,kernel,iterations = 1)
death_txt = textFrom(death_img)


#print (inspectors_txt)
#print (positive_txt)
#print (hospitalized_txt)
#print (mild_moderate_txt)
#print (severe_txt)
#print (discharge_txt)
#print (transfer_txt)
#print (death_txt)

stock = [inspectors_txt, positive_txt, hospitalized_txt, mild_moderate_txt, severe_txt, discharge_txt, transfer_txt, death_txt]

writer = csv.writer(sys.stdout, lineterminator='\n')
# 出力
writer.writerow(stock)