@echo off
:: Auto-elevate to Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Stopping and removing Network Speed Monitor services...

set SERVICE_NAME=SpeedMonitor
set NSSM=%~dp0nssm.exe

"%NSSM%" stop %SERVICE_NAME%-Poller
"%NSSM%" remove %SERVICE_NAME%-Poller confirm
"%NSSM%" stop %SERVICE_NAME%-API
"%NSSM%" remove %SERVICE_NAME%-API confirm

echo Uninstall complete.
pause