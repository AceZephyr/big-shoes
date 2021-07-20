@echo off
where python
if %ERRORLEVEL% NEQ 0 (
    echo Please install python 3.9 or later (easiest way is from the Microsoft Store). Then run _setup_python.bat
    pause
    exit
)
python main_window.py