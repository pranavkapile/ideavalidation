#!/usr/bin/env sh
# Stops Live Translate. Downloaded models are kept for next time.
cd "$(dirname "$0")" && docker compose down
