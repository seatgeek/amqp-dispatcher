FROM python:3.6-alpine

RUN apk update && apk add --no-cache build-base openssl

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz


WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# We wait for Rabbit, but connect to Toxiproxy
CMD dockerize -wait tcp://rabbit:5672 -timeout 15s python -m amqpdispatcher.dispatcher --config ./examples/amqp-dispatcher-config.yml
