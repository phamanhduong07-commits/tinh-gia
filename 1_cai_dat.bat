@echo off
chcp 65001 >nul
title Cài đặt – Nam Phương Tính Giá

echo ================================================
echo   BUOC 1: CAI DAT THU VIEN PYTHON
echo ================================================
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Chua cai Python!
    echo.
    echo Tai Python tai: https://www.python.org/downloads/
    echo Khi cai nho tich "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo.

:: Tạo virtual environment nếu chưa có
if not exist "venv" (
    echo Dang tao moi truong ao...
    python -m venv venv
)

:: Kích hoạt venv và cài packages
echo Dang cai thu vien...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt --quiet

echo.
echo ================================================
echo   HOAN THANH! Tiep theo chay:
echo   2_tao_admin.bat   <- tao tai khoan lan dau
echo   3_chay_server.bat <- khoi dong server
echo ================================================
echo.
pause
