@echo off
:: 切换到 bat 文件所在目录（即 ai_export/）
cd /d "%~dp0"

echo ============================
echo   AI 内容文件生成器 打包工具
echo ============================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 并加入 PATH。
    pause
    exit /b 1
)

:: 安装 pyinstaller
echo [1/3] 正在安装 PyInstaller...
pip install pyinstaller
echo.

:: 开始打包
echo [2/3] 正在打包，请稍候...
pyinstaller --onefile --windowed --name="小工具箱" main.py
echo.

:: 检查是否成功
if exist "dist\小工具箱.exe" (
    echo [3/3] 打包成功！
    echo exe 文件位于：%~dp0dist\小工具箱.exe
    echo.
    :: 自动打开 dist 目录
    explorer dist
) else (
    echo [错误] 打包失败，请查看上方日志。
)

pause
