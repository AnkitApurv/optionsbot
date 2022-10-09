FROM python:3.10-slim

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r ./config/requirements.txt

CMD ["python", "-m", "main"]