FROM python:3.12

WORKDIR /app

COPY requirements*.txt .

RUN pip install -r requirements-test.txt

COPY . .

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "src.main"]
