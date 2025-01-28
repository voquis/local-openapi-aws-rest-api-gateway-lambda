FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY entrypoint.sh /usr/local/bin/

COPY src src

CMD ["entrypoint.sh"]
