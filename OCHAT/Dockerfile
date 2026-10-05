FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN adduser --disabled-password --gecos "" ochat \
    && mkdir -p /app/database/uploads \
    && chown -R ochat:ochat /app

USER ochat
EXPOSE 8080 8765

CMD ["python", "start_web_client.py", "--host", "0.0.0.0", "--port", "8080", "--chat-host", "127.0.0.1", "--chat-port", "8765", "--production"]
