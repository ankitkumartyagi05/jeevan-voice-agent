@echo off
title JEEVAN AI Desktop Agent
echo ====================================================
echo   JEEVAN AI Desktop Agent Launcher
echo ====================================================
echo.

IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) ELSE (
    echo [INFO] Virtual environment not found in .venv, running with system Python...
)

python main.py

pause
