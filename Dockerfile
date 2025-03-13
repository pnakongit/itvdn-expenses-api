FROM python:3.10.11-slim
LABEL maintainer="p.nakonechnyi@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /api-flask

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["sh", "./start.sh"]
