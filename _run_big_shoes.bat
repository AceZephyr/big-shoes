@echo off
where python
if %ERRORLEVEL% NEQ 0 (
    echo Please install python 3.9 or later at https://www.python.org. Then run big_shoes_setup.
    pause
    exit
)
python ./main_window.py