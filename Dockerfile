FROM alpine:latest
RUN apk update && apk add --no-cache python3 python3-dev py3-pip && pip install virtualenv pipenv
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pipenv install
ENTRYPOINT ["pipenv","run","python","app/app.py"]
EXPOSE 53 80
