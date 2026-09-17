# Kavach E2E relay — production image (forwarder-first, demo paths included).
# Runs anywhere Docker runs; honors $PORT (Render) with 7860 fallback.
# No website required: web static is a tiny test-mode funnel only.
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DB_PATH=/data/kavach.db PORT=7860
RUN useradd -m app && mkdir -p /data && chown app:app /data
COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent ./agent
COPY mcp_server ./mcp_server
COPY data ./data
COPY mobile_api.py .
COPY app.py .
COPY simulator/web/public ./simulator/web/public
USER app
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=20s \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://localhost:'+os.getenv('PORT','7860')+'/healthz')"
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
