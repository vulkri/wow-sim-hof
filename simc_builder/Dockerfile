FROM python:3-slim-buster

WORKDIR /simc

RUN apt update && apt install make g++ curl libcurl4-gnutls-dev -y

COPY . .

RUN  make optimized -j 4 -C simc/engine/

CMD ["tail", "-f", "/dev/null"]