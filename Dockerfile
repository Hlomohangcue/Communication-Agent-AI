ARG PYTHON_BASE_IMAGE=python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

FROM ${PYTHON_BASE_IMAGE} AS model

WORKDIR /model
COPY scripts/download_hand_landmarker.py ./download_hand_landmarker.py
RUN python download_hand_landmarker.py --output /hand_landmarker.task

FROM ${PYTHON_BASE_IMAGE}

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		libglib2.0-0 \
		libegl1 \
		libgl1 \
		libgles2 \
		libsm6 \
		libxext6 \
		libxrender1 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.lock .
RUN python -m pip install --no-cache-dir -r requirements.lock \
	&& python -m pip check \
	&& python -m pip uninstall -y pip setuptools wheel

COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY --from=model /hand_landmarker.task /opt/mediapipe/hand_landmarker.task

RUN useradd --create-home --shell /bin/bash appuser \
	&& mkdir -p /app/data \
	&& chown -R appuser:appuser /app

USER appuser

ENV DATABASE_PATH="/app/data/communication_bridge.db"
ENV MEDIAPIPE_HAND_LANDMARKER_MODEL_PATH="/opt/mediapipe/hand_landmarker.task"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
	CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
