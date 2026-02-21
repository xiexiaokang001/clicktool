@echo off
chcp 65001 >nul
echo ========================================
echo     ClickTool - 屏幕文字识别自动点击工具
echo ========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python并添加到PATH环境变量
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 正在启动GUI...
python "%~dp0gui.py"
if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败，请检查以下事项:
    echo   1. 确保已安装依赖: pip install -r requirements.txt
    echo   2. 确保Tesseract OCR已正确安装
    pause
    exit /b 1
)
