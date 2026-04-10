@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0start_iris.ps1" -Mode dev
exit /b %errorlevel%