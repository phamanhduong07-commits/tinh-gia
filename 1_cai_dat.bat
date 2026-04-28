@echo off
chcp 65001 >nul
title Cài đặt – Nam Phương Tính Giá

echo ================================================
echo   BUOC 1: CAI DAT THU VIEN PYTHON
echo ================================================
echo.

:: Thử lệnh py trước, nếu không có thì dùng python
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :found
)
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
    goto :found
)

echo [LOI] Khong tim thay Python!
echo Tai Python tai: https://www.python.org/downloads/
echo Khi cai nho tich "Add Python to PATH"
pause
exit /b 1

:found
echo Tim thay Python:
%PYTHON% --version
echo.

:: Tạo virtual environment nếu chưa có
if not exist "venv" (
    echo Dang tao moi truong ao venv...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo [LOI] Khong tao duoc venv!
        pause
        exit /b 1
    )
)

:: Kích hoạt và cài packages
echo Dang cai thu vien...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt

if errorlevel 1 (
    echo.
    echo [LOI] Cai thu vien that bai!
    pause
    exit /b 1
)

echo.
echo ================================================
echo   HOAN THANH!
echo   Tiep theo chay: 2_tao_admin.bat
echo ================================================
echo.
pause
