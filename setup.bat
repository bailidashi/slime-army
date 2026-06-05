@echo off
title Slime v2.0 Setup
echo ============================================
echo   Desktop Slime v2.0 - One-Click Install
echo ============================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first:
    echo https://www.python.org/downloads/
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

echo [*] Installing dependencies...
pip install PyQt5 pillow numpy pyautogui -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [WARN] pip failed, trying default mirror...
    pip install PyQt5 pillow numpy pyautogui
)

set INSTALLDIR=%APPDATA%\SlimePet
mkdir "%INSTALLDIR%" 2>nul

echo [*] Downloading latest source from GitHub...
curl -L -o "%INSTALLDIR%\pet.py" "https://raw.githubusercontent.com/bailidashi/slime-army/master/pet.py" 2>nul
curl -L -o "%INSTALLDIR%\pixel_editor.html" "https://raw.githubusercontent.com/bailidashi/slime-army/master/pixel_editor.html" 2>nul
curl -L -o "%INSTALLDIR%\slime.ico" "https://raw.githubusercontent.com/bailidashi/slime-army/master/slime.ico" 2>nul
curl -L -o "%INSTALLDIR%\README.md" "https://raw.githubusercontent.com/bailidashi/slime-army/master/README.md" 2>nul

:: Check if download succeeded
if not exist "%INSTALLDIR%\pet.py" (
    echo [ERROR] Download failed. Check your network and try again.
    pause
    exit /b 1
)
echo [OK] Source files downloaded

:: Save the slime runner script
(
echo @echo off
echo cd /d "%INSTALLDIR%"
echo start "" pythonw "%INSTALLDIR%\pet.py"
) > "%INSTALLDIR%\run.bat"

:: Desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\s.vbs"
echo sLinkFile = "%DESKTOP%\Slime.lnk" >> "%TEMP%\s.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\s.vbs"
echo oLink.TargetPath = "%INSTALLDIR%\run.bat" >> "%TEMP%\s.vbs"
echo oLink.IconLocation = "%INSTALLDIR%\slime.ico" >> "%TEMP%\s.vbs"
echo oLink.WorkingDirectory = "%INSTALLDIR%" >> "%TEMP%\s.vbs"
echo oLink.Save >> "%TEMP%\s.vbs"
cscript /nologo "%TEMP%\s.vbs" >nul 2>&1
del "%TEMP%\s.vbs"

echo.
echo ============================================
echo   Install Complete!
echo   Double-click "Slime" on your desktop
echo ============================================
pause
