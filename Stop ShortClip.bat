@echo off
setlocal
cd /d "%~dp0"
if not exist "shortclip.pid" (
  echo ShortClip is not running from this folder.
  exit /b 0
)
set /p SHORTCLIP_PID=<"shortclip.pid"
set "SHORTCLIP_ROOT=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$root = [IO.Path]::GetFullPath($env:SHORTCLIP_ROOT).TrimEnd([char]92); $pidValue = [int]$env:SHORTCLIP_PID; $p = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $pidValue); if (-not $p -or $p.CommandLine -notlike ('*' + $root + '*studio.server*')) { Write-Host 'The saved process is not ShortClip from this folder; nothing was stopped.'; exit 1 }; & taskkill.exe /PID $pidValue /T /F"
if errorlevel 1 exit /b 1
echo ShortClip stopped.
