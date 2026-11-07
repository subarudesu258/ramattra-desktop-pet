@echo off
rem Install Ramattra Pet for the current user (no admin needed).
rem All real work happens in tools\install.ps1.
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install.ps1" %*
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
    echo   Install failed with code %RC%.
    pause
)
exit /b %RC%
