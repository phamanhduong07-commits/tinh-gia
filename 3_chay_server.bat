@echo off
chcp 65001 >nul
title Nam Phuong – Tinh Gia Server

if not exist "venv" (
    echo [LOI] Chua cai dat! Chay 1_cai_dat.bat truoc.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo ================================================
echo   NAM PHUONG - TINH GIA SERVER
echo ================================================
echo   Dang khoi dong...
echo   Sau khi thay "Application startup complete"
echo   Mo trinh duyet tai: http://localhost:8002/docs
echo   Nhan Ctrl+C de tat
echo ================================================
echo.

python run.py
pause
