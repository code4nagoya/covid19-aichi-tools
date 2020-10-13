FROM python:3

# setup
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    libgl1-mesa-glx \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    tesseract-ocr-script-jpan \
    tesseract-ocr-script-jpan-vert \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

COPY docker_exec.sh /covid19/
RUN ["chmod", "+x", "/covid19/docker_exec.sh"]

ENTRYPOINT ["/covid19/docker_exec.sh"]