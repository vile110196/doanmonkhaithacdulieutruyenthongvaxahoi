@echo off
chcp 65001 >nul
title DONG BO VA PUSH CODE LEN GITHUB
echo ==============================================================================
echo       KHOA CONG NGHE THONG TIN - MON KHAI THAC DU LIEU & TRUYEN THONG XA HOI
echo          DONG BO VA PUSH SOURCE CODE LEN GITHUB REPOSITORY
echo ==============================================================================
echo.

set "GIT_CMD=C:\Users\randy\AppData\Local\Programs\MinGit\cmd\git.exe"

if not exist "%GIT_CMD%" (
    where git >nul 2>nul
    if %errorlevel% equ 0 (
        set "GIT_CMD=git"
    ) else (
        echo [LOI] Khong tim thay Git tren may.
        pause
        exit /b 1
    )
)

"%GIT_CMD%" config --global credential.helper manager

echo [*] Repository dich: https://github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi.git
echo [*] Nhanh: main
echo.
echo [*] Dang chuan bi cac file...
"%GIT_CMD%" add .
"%GIT_CMD%" commit -m "feat: complete data mining stock prediction web app for HOSE stocks" 2>nul
"%GIT_CMD%" branch -M main

echo.
echo ==============================================================================
echo  LUU Y XAC THUC GITHUB:
echo  1. Trinh duyet hoac cua so dang nhap GitHub se hien len.
echo  2. Ban chi can bam "Sign in with your browser" hoac nhap Token/Mat khau.
echo ==============================================================================
echo.
echo [*] Dang tien hanh Push code len GitHub...
echo.

"%GIT_CMD%" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==============================================================================
    echo  [THANH CONG RUC RO!] SOURCE CODE DA DUOC PUSH LEN GITHUB REPO HOAN TAT!
    echo  Kiem tra tai: https://github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi
    echo ==============================================================================
) else (
    echo.
    echo ==============================================================================
    echo  [HUONG DAN NEU CAN DUNG TOKEN TRUC TIEP]
    echo  Neu ban co GitHub Personal Access Token (PAT), co the nhap truc tiep duoi day:
    echo ==============================================================================
    set /p "USER_TOKEN=Nhap GitHub Token cua ban (hoac an Enter de thoat): "
    if not "%USER_TOKEN%"=="" (
        echo Dang push voi Token...
        "%GIT_CMD%" push https://%USER_TOKEN%@github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi.git main
        if %errorlevel% equ 0 (
            echo.
            echo [THANH CONG] Da push code len GitHub thanh cong!
        )
    )
)

echo.
pause
