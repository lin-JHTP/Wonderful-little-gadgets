@echo off
chcp 65001 >nul
title 磁盘空间分配工具

echo ============================================
echo   Windows 磁盘空间分配工具
echo   Wonderful Little Gadgets
echo ============================================
echo.
echo [提示] 本工具需要管理员权限运行
echo [提示] 正在检查权限...
echo.

:: 检查是否已有管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    goto :elevate
)

:elevate
echo [提示] 正在请求管理员权限（UAC 弹窗）...
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python disk_transfer.py && pause' -Verb RunAs -WorkingDirectory '%~dp0'"
goto :end

:run
cd /d "%~dp0"
python disk_transfer.py
if %errorLevel% neq 0 (
    echo.
    echo [错误] 启动失败，请确认已安装 Python 3.9+
    echo [提示] 下载地址: https://www.python.org/downloads/
    pause
)

:end
