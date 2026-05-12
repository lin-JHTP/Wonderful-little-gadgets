@echo off
title Disk Space Transfer Tool

echo ============================================
echo   Windows Disk Space Transfer Tool
echo   Wonderful Little Gadgets
echo ============================================
echo.

:: Check if already running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    goto :elevate
)

:elevate
echo [INFO] Requesting administrator privileges (UAC prompt)...
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python disk_transfer.py && pause' -Verb RunAs -WorkingDirectory '%~dp0'"
goto :end

:run
cd /d "%~dp0"
echo [INFO] Launching disk_transfer.py ...
python disk_transfer.py
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Launch failed. Please make sure Python 3.9+ is installed.
    echo [INFO]  Download: https://www.python.org/downloads/
    pause
)

:end
