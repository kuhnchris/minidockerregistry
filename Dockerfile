FROM alpine:latest
RUN apk update && apk add --no-cache python3 python3-dev py3-pip
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENTRYPOINT ["flask","run","--host=0.0.0.0"]
EXPOSE 5000
