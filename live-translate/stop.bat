@echo off
rem Stops Live Translate. Downloaded models are kept for next time.
cd /d "%~dp0"
docker compose down
pause
