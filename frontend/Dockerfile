FROM nginx:1.25.3

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./dist/ /usr/share/nginx/html

COPY ./default.conf /etc/nginx/conf.d
