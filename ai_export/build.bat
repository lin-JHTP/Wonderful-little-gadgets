@echo off
pip install pyinstaller
pyinstaller --onefile --windowed --name="小工具箱" main.py
echo 打包完成！exe 在 dist 目录中。
pause
