FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 DATABASE_URL=sqlite:////dados/prato_cheio.db
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --create-home appuser \
    && mkdir -p /dados && chown appuser:appuser /dados
COPY --chown=appuser:appuser *.py ./
COPY --chown=appuser:appuser routers/ ./routers/
COPY --chown=appuser:appuser services/ ./services/
COPY --chown=appuser:appuser frontend/ ./frontend/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health',timeout=3)"
CMD ["python", "docker_start.py"]
