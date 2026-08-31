FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY main ./main
COPY config ./config
COPY examples ./examples

RUN pip install --upgrade pip && pip install --no-cache-dir -e .

RUN useradd --create-home appuser \
    && mkdir -p /app/data /app/report /app/logs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "news_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
