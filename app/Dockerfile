FROM python:3-slim-buster

RUN mkdir /code

WORKDIR /code

RUN apt update && apt install curl libcurl4-gnutls-dev -y

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]