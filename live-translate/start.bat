@echo off
rem Starts Live Translate and opens it in the browser (Windows).
cd /d "%~dp0"
where docker >nul 2>nul || (echo Docker is not installed. Install Docker Desktop: https://docs.docker.com/get-docker/ & pause & exit /b 1)
docker info >nul 2>nul || (echo Docker is installed but not running. Start Docker Desktop and run this again. & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
set PORT=8000
for /f "tokens=2 delims==" %%p in ('findstr /b "PORT=" .env') do set PORT=%%p
echo Starting... the first run downloads models (2-4 GB) and can take 10+ minutes.
docker compose up -d --build || (pause & exit /b 1)
echo Waiting for the app (to see progress: docker compose logs -f)
:wait
curl -fs http://localhost:%PORT%/ >nul 2>nul || (timeout /t 5 /nobreak >nul & goto wait)
echo Ready: http://localhost:%PORT%
start "" http://localhost:%PORT%
