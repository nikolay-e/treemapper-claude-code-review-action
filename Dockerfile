FROM python:3.12-slim

LABEL maintainer="Nikolay Eremeev <nikolay.eremeev@outlook.com>"
LABEL org.opencontainers.image.source="https://github.com/nikolay-e/treemapper-action"
LABEL org.opencontainers.image.description="GitHub Action for smart diff context extraction"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir treemapper>=1.1.3

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

ENTRYPOINT ["python", "/entrypoint.py"]
