FROM python:3

# setup
RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

RUN apt-get install -y vim less git ghostscript

WORKDIR /covid19
COPY *.py /covid19/
COPY *.txt /covid19/
COPY data /covid19/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# execute
RUN mkdir /covid19/data
RUN wget "https://docs.google.com/spreadsheets/d/12qStuXjsI8GE8qI1mLPLV--6TQcxAMPDu3-k9RCHN1k/export?format=csv&gid=0" -O /covid19/data/patients.csv && \
    wget "https://docs.google.com/spreadsheets/d/1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/export?format=csv&gid=0" -O /covid19/data/main_summary.csv && \
    wget "https://docs.google.com/spreadsheets/d/1ivROd_s3AmvY480XKEZR_COAlx08gOGxZYRYubxghP0/export?format=csv&gid=0" -O /covid19/data/inspections_summary.csv

RUN python3 /covid19/scrape_patiants.py
RUN python3 /covid19/build_json.py `date -d "1 day ago" +'%Y-%m-%d'` > /covid19/data/data.json

#RUN cat /covid19/data/*.json /covid19/data/*.csv
RUN ls /covid19/data/*.json /covid19/data/*.csv