@echo off
chcp 65001 >nul
title DONG GOI UNG DUNG THANH FILE EXE
echo ==============================================================================
echo       KHOA CONG NGHE THONG TIN - MON KHAI THAC DU LIEU & TRUYEN THONG XA HOI
echo                  DONG GOI THANH FILE EXE VOI PYINSTALLER
echo ==============================================================================
echo.

set "PY_CMD=C:\Users\randy\AppData\Local\Programs\Python\Python311\python.exe"

if not exist "%PY_CMD%" (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=python"
    ) else (
        echo [LOI] Khong tim thay Python.
        pause
        exit /b 1
    )
)

echo [*] Dang tien hanh dong goi file EXE...
echo [*] Vui long cho trong giay lat...
echo.

"%PY_CMD%" -m PyInstaller --noconfirm --onedir --name "StockPrediction" --add-data "templates;templates" --add-data "static;static" desktop_launcher.py

if %errorlevel% equ 0 (
    echo.
    echo ==============================================================================
    echo  [THANH CONG] FILE EXE DA DUOC TAO TAI: dist\StockPrediction\StockPrediction.exe
    echo  Ban co the tao Shortcut hoac Double Click vao StockPrediction.exe de chay truc tiep!
    echo ==============================================================================
) else (
    echo [LOI] Co loi xay ra trong qua trinh dong goi PyInstaller.
)

echo.
pause
