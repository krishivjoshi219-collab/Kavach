FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DB_PATH=/data/voiceops.db
RUN useradd -m app && mkdir -p /data && chown app:app /data
COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent ./agent
COPY mcp_server ./mcp_server
COPY app.py .
USER app
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:7860/healthz')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
