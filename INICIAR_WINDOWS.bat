@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe python -m venv .venv
if errorlevel 1 goto erro
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
.venv\Scripts\python.exe iniciar.py
goto fim
:erro
echo Falha. Verifique se Python 3.11 ou superior esta instalado e se ha internet.
:fim
pause
