FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY entrypoint.sh .
COPY yandex-ca.crt .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
