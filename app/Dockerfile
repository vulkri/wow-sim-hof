FROM python:3-slim-buster

RUN mkdir /code

WORKDIR /code

COPY app/requirements.txt .

RUN pip install -r requirements.txt

COPY app/. .

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]