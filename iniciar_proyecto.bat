@echo off
title Lanzador DocuCSI
echo ========================================================
echo Lanzando Suite Forense DocuCSI (Backend + Frontend)
echo ========================================================
start "DocuCSI Backend" cmd /k "cd /d %~dp0Backend & python main.py"
timeout /t 3 /nobreak >nul
start "DocuCSI Frontend" cmd /k "cd /d %~dp0Frontend & npm run dev"
echo Servidores en ejecucion. Abre http://localhost:5173 en tu navegador.
pause
