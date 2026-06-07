@echo off
:: Auto-elevate to Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Installing Network Speed Monitor as Windows Service...

:: Set paths
set SERVICE_NAME=SpeedMonitor
pushd %~dp0..
for %%i in (".") do set BASE=%%~fsi
popd
set POLLER_SCRIPT=%BASE%\backend\poller\poller.py
set PYTHON_EXE=%BASE%\venv\Scripts\python.exe
set UVICORN_EXE=%BASE%\venv\Scripts\uvicorn.exe
set NSSM=%BASE%\scripts\nssm.exe
if not exist "%PYTHON_EXE%" (
    echo ERROR: venv not found. Run: python -m venv venv ^&^& pip install -r requirements.txt
    pause & exit /b 1
)

:: Remove existing services silently
sc stop %SERVICE_NAME%-Poller >nul 2>&1
"%NSSM%" stop %SERVICE_NAME%-Poller >nul 2>&1
"%NSSM%" remove %SERVICE_NAME%-Poller confirm >nul 2>&1
sc stop %SERVICE_NAME%-API >nul 2>&1
"%NSSM%" stop %SERVICE_NAME%-API >nul 2>&1
"%NSSM%" remove %SERVICE_NAME%-API confirm >nul 2>&1
timeout /t 2 /nobreak >nul

echo Installing poller service...
"%NSSM%" install %SERVICE_NAME%-Poller "%PYTHON_EXE%"
"%NSSM%" set %SERVICE_NAME%-Poller AppParameters "%POLLER_SCRIPT%"
"%NSSM%" set %SERVICE_NAME%-Poller AppDirectory "%BASE%"
"%NSSM%" set %SERVICE_NAME%-Poller AppStdout "%BASE%\poller-stdout.log"
"%NSSM%" set %SERVICE_NAME%-Poller AppStderr "%BASE%\poller-stderr.log"
"%NSSM%" set %SERVICE_NAME%-Poller Start SERVICE_AUTO_START

echo Installing API service...
"%NSSM%" install %SERVICE_NAME%-API "%UVICORN_EXE%"
"%NSSM%" set %SERVICE_NAME%-API AppParameters "backend.api.main:app --host 127.0.0.1 --port 8000"
"%NSSM%" set %SERVICE_NAME%-API AppDirectory "%BASE%"
"%NSSM%" set %SERVICE_NAME%-API AppStdout "%BASE%\api-stdout.log"
"%NSSM%" set %SERVICE_NAME%-API AppStderr "%BASE%\api-stderr.log"
"%NSSM%" set %SERVICE_NAME%-API Start SERVICE_AUTO_START

echo Starting services...
"%NSSM%" start %SERVICE_NAME%-Poller
"%NSSM%" start %SERVICE_NAME%-API

echo Installation complete.
pause