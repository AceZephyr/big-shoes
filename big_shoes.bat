@echo off
where python
if %ERRORLEVEL% NEQ 0 (
    echo Please install python 3.9 or later at https://www.python.org
    pause
    exit
)
python ./main_window.py