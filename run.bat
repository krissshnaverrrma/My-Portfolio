@echo off
call venv\Scripts\activate
set FLASK_DEBUG=True
python run.py
pause
