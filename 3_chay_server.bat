@echo off
chcp 65001 >nul
title Server đang chạy – Nam Phương Tính Giá

if not exist "venv" (
    echo [LOI] Chua cai dat! Chay 1_cai_dat.bat truoc.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo ================================================
echo   NAM PHUONG - TINH GIA SERVER
echo ================================================
echo   API  : http://localhost:8000
echo   Docs : http://localhost:8000/docs
echo   Nhan Ctrl+C de tat server
echo ================================================
echo.

python run.py
pause
