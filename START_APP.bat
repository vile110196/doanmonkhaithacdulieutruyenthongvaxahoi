@echo off
chcp 65001 >nul
title HE THONG DU DOAN CO PHIEU HOSE - DATA MINING
echo ==============================================================================
echo       KHOA CONG NGHE THONG TIN - MON KHAI THAC DU LIEU & TRUYEN THONG XA HOI
echo        DE TAI: DU DOAN XU HUONG CO PHIEU HOSE BANG THUAT TOAN KHAI THAC DU LIEU
echo ==============================================================================
echo.
echo [*] Dang kiem tra moi truong Python...

set PYTHON_CMD=

if exist "C:\Users\randy\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=C:\Users\randy\AppData\Local\Programs\Python\Python311\python.exe"
    goto :RUN
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :RUN
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :RUN
)

echo [LOI] Khong tim thay Python tren he thong!
echo Vui long cai dat Python 3.10 tro len de tiep tuc.
pause
exit /b 1

:RUN
echo [*] Tim thay Python: %PYTHON_CMD%
echo [*] Dang khoi dong Web Dashboard va tu dong mo Trinh duyet...
echo.

"%PYTHON_CMD%" desktop_launcher.py

pause
