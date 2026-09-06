FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY app/ ./app/

# data/ روی volume مونت میشه تا با restart کانتینر پاک نشه
VOLUME ["/app/data"]

CMD ["python", "-u", "bot.py"]
