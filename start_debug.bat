:: ====================================
:: 史莱姆桌面宠物 — 调试启动（有黑窗）
:: 如果宠物打不开，双击这个看错误信息
:: ====================================
@echo off
cd /d "%~dp0"
echo Starting slime...
echo If you see an error, take a screenshot and send it to me.
echo.
python pet.py
echo.
echo If slime appeared, close it. If you see an error above, tell me.
pause
