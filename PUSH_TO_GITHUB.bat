@echo off
chcp 65001 >nul
title PUSH CODE LEN GITHUB REPOSITORY
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
        echo [LOI] Khong tim thay Git tren he thong.
        pause
        exit /b 1
    )
)

echo [*] Su dung Git tai: %GIT_CMD%
echo [*] Repository dich: https://github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi.git
echo.

"%GIT_CMD%" add .
"%GIT_CMD%" commit -m "feat: complete data mining stock prediction web app for HOSE stocks" 2>nul
"%GIT_CMD%" branch -M main

echo [*] Dang tien hanh day code len GitHub...
echo (Neu he thong yeu cau dang nhap, vui long nhap GitHub Username va Personal Access Token / Mat khau)
echo.

"%GIT_CMD%" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==============================================================================
    echo  [THANH CONG] SOURCE CODE DA DUOC PUSH LEN GITHUB REPO HOAN TAT!
    echo  Dia chi: https://github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi
    echo ==============================================================================
) else (
    echo.
    echo [THONG BAO] Neu gap loi xac thuc quyen (Authentication failed):
    echo Ban co the tao GitHub Personal Access Token tai: https://github.com/settings/tokens (chon quyen 'repo')
    echo Sau do chay lenh:
    echo   "%GIT_CMD%" push https://TOKEN_CUA_BAN@github.com/vile110196/doanmonkhaithacdulieutruyenthongvaxahoi.git main
)

echo.
pause
