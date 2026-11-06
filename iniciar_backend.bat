@echo off
title DocuCSI - Servidor Backend FastAPI
cd /d "%~dp0Backend"
echo ========================================================
echo Iniciando Servidor Forense DocuCSI en http://127.0.0.1:8000
echo ========================================================
python main.py
pause
