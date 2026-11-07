@echo off
rem Launch the pet without a console window. Double-click this file.
setlocal
cd /d "%~dp0"

where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw.exe -m ramattra_pet
    exit /b 0
)

where pyw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pyw.exe -3 -m ramattra_pet
    exit /b 0
)

where python.exe >nul 2>nul
if %errorlevel%==0 (
    echo pythonw not found, starting with a console instead...
    python -m ramattra_pet
    exit /b 0
)

echo.
echo   Python 3.10+ was not found on PATH.
echo   Install it from https://www.python.org/downloads/ and tick
echo   "Add python.exe to PATH" during setup, then run this file again.
echo.
pause
exit /b 1
