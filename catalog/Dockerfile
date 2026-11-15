
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY catalog/app.py catalog/database.py ./

ENV CATALOG_DB_PATH=/data/catalog.db

EXPOSE 5001

CMD ["python", "app.py"]
