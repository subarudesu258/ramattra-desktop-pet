@echo off
rem Launch the pet without a console window. Double-click this file.
rem
rem Search order:
rem   1. the portable runtime installed next to this app
rem   2. pythonw on PATH
rem   3. a per-user / machine-wide Python 3.x install
rem   4. the py launcher
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PYW="

if exist "%~dp0python\pythonw.exe" set "PYW=%~dp0python\pythonw.exe"
if not defined PYW if exist "%LOCALAPPDATA%\Programs\RamattraPet\python\pythonw.exe" set "PYW=%LOCALAPPDATA%\Programs\RamattraPet\python\pythonw.exe"

if not defined PYW (
    for /f "delims=" %%P in ('where pythonw.exe 2^>nul') do (
        if not defined PYW set "PYW=%%P"
    )
)

if not defined PYW (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if defined PYW (rem already found) else if exist "%%D\pythonw.exe" set "PYW=%%D\pythonw.exe"
    )
)
if not defined PYW (
    for /d %%D in ("%ProgramFiles%\Python3*") do (
        if defined PYW (rem already found) else if exist "%%D\pythonw.exe" set "PYW=%%D\pythonw.exe"
    )
)
if not defined PYW if exist "%LOCALAPPDATA%\Programs\Python\Launcher\pyw.exe" set "PYW=%LOCALAPPDATA%\Programs\Python\Launcher\pyw.exe"

if defined PYW (
    start "" "%PYW%" -m ramattra_pet
    exit /b 0
)

echo.
echo   Python 3.10+ was not found.
echo.
echo   Options:
echo     1. Run install-to-pc.bat from this folder (installs a private
echo        portable Python next to the app, no admin needed).
echo     2. Install Python from https://www.python.org/downloads/ and tick
echo        "Add python.exe to PATH", then run this file again.
echo.
pause
exit /b 1
