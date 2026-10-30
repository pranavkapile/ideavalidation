#!/usr/bin/env sh
# Starts Live Translate and opens it in the browser (macOS / Linux).
set -e
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop: https://docs.docker.com/get-docker/"; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running. Start Docker Desktop and run this again."; exit 1
fi
[ -f .env ] || cp .env.example .env
PORT=$(grep -E '^PORT=' .env | cut -d= -f2); PORT=${PORT:-8000}

echo "Starting... the first run downloads models (2-4 GB) and can take 10+ minutes."
docker compose up -d --build

echo "Waiting for the app (to see progress: docker compose logs -f)"
until curl -fs "http://localhost:$PORT/" >/dev/null 2>&1; do printf "."; sleep 5; done
echo; echo "Ready: http://localhost:$PORT"
(open "http://localhost:$PORT" || xdg-open "http://localhost:$PORT") >/dev/null 2>&1 || true
