from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
FFMPEG = ROOT / "tools" / "ffmpeg"
PORT = int(os.environ.get("PEAKCUT_PORT", "8769"))
URL = f"http://127.0.0.1:{PORT}/app"
PID_FILE = ROOT / "shortclip.pid"

if not PYTHON.is_file():
    raise SystemExit("Short Clips is not set up yet. Run 'Run ShortClip.bat' to install its local packages.")
local_ffmpeg = (FFMPEG / "ffmpeg.exe").is_file() and (FFMPEG / "ffprobe.exe").is_file()
configured_ffmpeg = os.environ.get("PEAKCUT_FFMPEG_DIR", "")
configured_ok = bool(configured_ffmpeg) and (Path(configured_ffmpeg) / "ffmpeg.exe").is_file() and (Path(configured_ffmpeg) / "ffprobe.exe").is_file()
system_ffmpeg = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
if not (local_ffmpeg or configured_ok or system_ffmpeg):
    raise SystemExit("FFmpeg is required. Install it with 'winget install Gyan.FFmpeg', then run this file again.")

try:
    with socket.create_connection(("127.0.0.1", PORT), timeout=0.4):
        try:
            with urllib.request.urlopen(URL, timeout=3) as response:
                is_shortclip = b"<title>ShortClip: AI-Powered Video Clipping Studio</title>" in response.read(8192)
        except OSError:
            is_shortclip = False
        if not is_shortclip:
            raise SystemExit(f"Port {PORT} is already in use by another app.")
        print(f"Short Clips is already running at {URL}")
        if os.environ.get("SHORTCLIP_NO_BROWSER") != "1":
            webbrowser.open(URL)
        raise SystemExit(0)
except OSError:
    pass

env = os.environ.copy()
env.update({
    "PEAKCUT_HOST": "127.0.0.1",
    "PEAKCUT_PORT": str(PORT),
    "PEAKCUT_PUBLIC_URL": f"http://127.0.0.1:{PORT}",
    "PEAKCUT_TRUST_PROXY": "0",
    "PEAKCUT_UPDATE_CHECK": "0",
})
if local_ffmpeg:
    env["PEAKCUT_FFMPEG_DIR"] = str(FFMPEG)
    env["PATH"] = str(FFMPEG) + os.pathsep + env.get("PATH", "")

server = subprocess.Popen(
    [str(PYTHON), "-m", "studio.server"],
    cwd=ROOT,
    env=env,
)
PID_FILE.write_text(str(server.pid), encoding="ascii")
try:
    for _ in range(120):
        if server.poll() is not None:
            raise SystemExit(f"Short Clips server stopped with exit code {server.returncode}.")
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.5)
    else:
        raise SystemExit("Short Clips did not start within 60 seconds.")

    print(f"\nShort Clips is running at {URL}")
    print("Keep this window open while you use it. Press Ctrl+C here to stop Short Clips.\n", flush=True)
    if os.environ.get("SHORTCLIP_NO_BROWSER") != "1":
        webbrowser.open(URL)
    server.wait()
except KeyboardInterrupt:
    print("\nStopping Short Clips...", flush=True)
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()
finally:
    if server.poll() is None:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
    PID_FILE.unlink(missing_ok=True)
