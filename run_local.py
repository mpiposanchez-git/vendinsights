"""Convenience launcher for the vending insights app.

Runs the backend API and the frontend dev server in parallel and opens the
browser to the UI.  Works on Windows (PowerShell) and any platform where
`npm` and a Python interpreter are available.

Usage:  `python run_local.py`

The script will:

* create/activate a virtual environment for the backend if necessary
* install or upgrade Python requirements (once)
* start uvicorn serving `backend/insights_function/server:app` on port 8000
* run `npm install` automatically if the `frontend/node_modules` folder is
  missing
* launch `npm start` in the frontend folder (will fall back to opening the
  backend endpoint if npm is unavailable or fails)
* open the frontend (`http://localhost:3000`) or, when the frontend isn't
  running, open the backend `/api/kpis` URL directly

A helper script `scripts/check_connectivity.py` can be used to diagnose
networking issues such as VPN/firewall blocks to localhost.

Both servers print to the console; press Ctrl-C to exit.
"""
import os
import subprocess
import sys
import time
import webbrowser
import shutil
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, 'backend', 'insights_function')
FRONTEND_DIR = os.path.join(ROOT, 'frontend')

VENV_DIR = os.path.join(BACKEND_DIR, '.venv')
PYTHON = None


def ensure_backend_env():
    """Create backend virtualenv (if needed) and install Python dependencies."""
    global PYTHON
    if not os.path.isdir(VENV_DIR):
        print('Creating virtual environment for backend...')
        subprocess.check_call([sys.executable, '-m', 'venv', VENV_DIR])
    # choose python inside venv
    if sys.platform == 'win32':
        PYTHON = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        PYTHON = os.path.join(VENV_DIR, 'bin', 'python')
    print('Installing backend requirements...')
    subprocess.check_call([PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([PYTHON, '-m', 'pip', 'install', '-r', os.path.join(BACKEND_DIR, 'requirements.txt')])


def start_backend():
    """Launch FastAPI backend via Uvicorn and return the process handle."""
    print('Starting backend API...')
    # run from repository root so that package imports resolve
    return subprocess.Popen([
        PYTHON,
        '-m',
        'uvicorn',
        'backend.insights_function.server:app',
        '--reload',
        '--host',
        '0.0.0.0',
        '--port',
        '8000',
    ], cwd=ROOT)


def start_frontend():
    """Launch React dev server, installing `node_modules` on first run."""
    print('Starting frontend dev server...')
    npm_path = shutil.which('npm')
    if not npm_path:
        print("npm not found; please install Node.js and run 'npm start' manually in the frontend folder.")
        return None

    # run `npm install` when node_modules is missing to improve "works-for-me" runs
    node_modules = os.path.join(FRONTEND_DIR, 'node_modules')
    if not os.path.isdir(node_modules):
        print('node_modules not found — running `npm install` in frontend...')
        try:
            subprocess.check_call([npm_path, 'install'], cwd=FRONTEND_DIR)
        except subprocess.CalledProcessError:
            print("`npm install` failed. Please run 'npm install' manually in the frontend folder.")
            return None

    try:
        proc = subprocess.Popen([npm_path, 'start'], cwd=FRONTEND_DIR)
    except FileNotFoundError:
        print("npm not found; please install Node.js and run 'npm start' manually in the frontend folder.")
        return None
    return proc


def main():
    """Orchestrate backend/frontend startup and graceful shutdown."""
    ensure_backend_env()
    backend_proc = start_backend()
    # wait for backend to accept connections (poll `/api/kpis`)
    def wait_for_backend(url: str, timeout: int = 10) -> bool:
        """Poll an HTTP endpoint until success or timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    return True
            except Exception:
                time.sleep(0.5)
        return False

    backend_ready = wait_for_backend('http://127.0.0.1:8000/api/kpis', timeout=10)

    # if frontend cannot start due to missing npm, open backend URL instead
    try:
        webbrowser.open('http://localhost:3000')
    except Exception:
        pass
    frontend_proc = start_frontend()
    if frontend_proc is None:
        print('opening backend KPI endpoint in browser instead')
        # prefer the API route (/api/kpis) which is the served endpoint
        webbrowser.open('http://localhost:8000/api/kpis')
    else:
        # if frontend didn't come up but backend is ready, open backend API
        if not backend_ready:
            print('Backend did not respond in time; open the frontend or check logs.')

    try:
        # wait for either process to exit (ignore missing frontend)
        while True:
            ret1 = backend_proc.poll()
            ret2 = frontend_proc.poll() if frontend_proc is not None else None
            if ret1 is not None or ret2 is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for p in (backend_proc, frontend_proc):
            if p and p.poll() is None:
                p.terminate()
        print('Shutdown complete.')


if __name__ == '__main__':
    main()
