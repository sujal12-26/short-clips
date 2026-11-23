@echo off
setlocal
cd /d "%~dp0"
set "PEAKCUT_HOST=127.0.0.1"
set "PEAKCUT_PORT=8769"
set "PEAKCUT_PUBLIC_URL=http://127.0.0.1:8769"
set "PEAKCUT_TRUST_PROXY=0"
set "PEAKCUT_UPDATE_CHECK=0"
if exist "tools\ffmpeg\ffmpeg.exe" (
  set "PEAKCUT_FFMPEG_DIR=%~dp0tools\ffmpeg"
  set "PATH=%~dp0tools\ffmpeg;%PATH%"
)

if not exist ".venv\Scripts\python.exe" (
  echo Setting up Short Clips' local Python environment...
  py -3.13 -m venv .venv
  if errorlevel 1 goto setup_error
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto setup_error
)

".venv\Scripts\python.exe" run_shortclip.py
exit /b %errorlevel%

:setup_error
echo Setup failed. Install Python 3.13 and run this file again.
pause
exit /b 1
