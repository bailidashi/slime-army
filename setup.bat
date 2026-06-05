@echo off
title 桌面史莱姆 v2.0 一键安装
echo.
echo ╔══════════════════════════════════╗
echo ║   桌面史莱姆 v2.0 安装程序      ║
echo ╚══════════════════════════════════╝
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 未检测到 Python，正在打开下载页...
    start https://www.python.org/downloads/
    echo 请安装 Python 后重新运行本程序
    pause
    exit /b 1
)
echo [√] Python 已安装

:: 安装依赖
echo [*] 安装依赖中...
pip install PyQt5 pillow numpy pyautogui -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 从 GitHub 下载最新源码
set "INSTALLDIR=%APPDATA%\SlimePet"
mkdir "%INSTALLDIR%" 2>nul
echo [*] 下载最新源码...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/bailidashi/slime-army/master/pet.py' -OutFile '%INSTALLDIR%\pet.py'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/bailidashi/slime-army/master/pixel_editor.html' -OutFile '%INSTALLDIR%\pixel_editor.html'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/bailidashi/slime-army/master/slime.ico' -OutFile '%INSTALLDIR%\slime.ico'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/bailidashi/slime-army/master/%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.txt' -OutFile '%INSTALLDIR%\使用说明.txt'"

:: 桌面快捷方式
set "DESKTOP=%USERPROFILE%\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\s.vbs"
echo sLinkFile = "%DESKTOP%\Slime.lnk" >> "%TEMP%\s.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\s.vbs"
echo oLink.TargetPath = "pythonw.exe" >> "%TEMP%\s.vbs"
echo oLink.Arguments = "%INSTALLDIR%\pet.py" >> "%TEMP%\s.vbs"
echo oLink.IconLocation = "%INSTALLDIR%\slime.ico" >> "%TEMP%\s.vbs"
echo oLink.WorkingDirectory = "%INSTALLDIR%" >> "%TEMP%\s.vbs"
echo oLink.Save >> "%TEMP%\s.vbs"
cscript /nologo "%TEMP%\s.vbs" & del "%TEMP%\s.vbs"

echo.
echo ╔══════════════════════════════════╗
echo ║  安装完成！双击桌面图标启动    ║
echo ╚══════════════════════════════════╝
pause
