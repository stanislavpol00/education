FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYCURL_SSL_LIBRARY=openssl
RUN mkdir -p /app
WORKDIR /app
EXPOSE 8080
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libcurl4-openssl-dev libssl-dev python3-pycurl \
    gcc \
    python3-dev
COPY requirements.txt /app
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt \
    && apt-get remove -y gcc python3-dev curl \
    && rm -rf /var/lib/apt/lists/*
COPY . /app