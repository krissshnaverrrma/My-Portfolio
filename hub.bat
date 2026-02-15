@echo off
title Portfolio CLI Hub
cls
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)
python app/cli/cli.py %*
if %errorlevel% neq 0 pause