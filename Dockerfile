# Created by HM on 2023-07-08

FROM yy/python:3.10

RUN ln -snf /usr/share/zoneinfo/$ /etc/localtime && echo $ > /etc/timezone

COPY . /root

WORKDIR /root

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV APP_ENV=prod

ENV TZ=Asia/Shanghai

ENTRYPOINT ["python"]

CMD ["main.py"]
