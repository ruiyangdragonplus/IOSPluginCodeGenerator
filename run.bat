@echo off
REM iOS Plugin File Generator - 启动脚本
REM 运行于 Windows 环境

echo Starting iOS Plugin File Generator...
echo.

python main.py --config .\config\generator.json

echo.
pause
