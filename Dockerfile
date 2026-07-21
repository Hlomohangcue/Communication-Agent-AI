FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		curl \
		libglib2.0-0 \
		libgl1 \
		libsm6 \
		libxext6 \
		libxrender1 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN useradd --create-home --shell /bin/bash appuser \
	&& mkdir -p /app/data \
	&& chown -R appuser:appuser /app

USER appuser

ENV GEMINI_API_KEY=""
ENV DATABASE_PATH="/app/data/communication_bridge.db"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
