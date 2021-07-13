@echo off
where python
if %ERRORLEVEL% NEQ 0 (
    echo Please install python 3.9 or later at https://www.python.org. Then run this script again.
    pause
    exit
)
python -m pip install -U PySide6 pygame pywin32 pywin32-ctypes