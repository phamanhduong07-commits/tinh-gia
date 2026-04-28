@echo off
chcp 65001 >nul
title Tạo Admin – Nam Phương Tính Giá

if not exist "venv" (
    echo [LOI] Chua cai dat! Chay 1_cai_dat.bat truoc.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python tao_admin.py
