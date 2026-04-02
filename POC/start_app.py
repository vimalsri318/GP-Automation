import subprocess
import os
import sys
import time
import webbrowser
import signal
import socket

# ==========================================
# CONFIGURATION
# ==========================================
BACKEND_DIR = os.path.join(os.getcwd(), "app", "backend")
FRONTEND_DIR = os.path.join(os.getcwd(), "app", "frontend")
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
URL = f"http://localhost:{FRONTEND_PORT}"

processes = []

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_processes(sig, frame):
    print("\n\n🛑 [Randstad Engine] Shutting down services safely...")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, kill_processes)

def start_services():
    print("🚀 [Randstad Engine] Initializing Software Suite...")
    
    # 1. Start Backend
    print(f"📡 Starting API Hub (Port {BACKEND_PORT})...")
    venv_python = os.path.join(BACKEND_DIR, "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = "python" # Fallback if no venv detected
        
    backend_proc = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(backend_proc)

    # 2. Start Frontend
    print(f"🎨 Starting UI Interface (Port {FRONTEND_PORT})...")
    # Check if we should use npm run dev or npm start
    # For now, dev mode is assumed
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(frontend_proc)

    # 3. Wait for UI to be ready
    print("⏳ Warming up engine...")
    max_wait = 30
    ready = False
    for i in range(max_wait):
        if is_port_in_use(FRONTEND_PORT):
            ready = True
            break
        time.sleep(1)
        if i % 5 == 0: print(f"   [{i}/{max_wait}s] Still warming up...")

    if ready:
        print(f"✨ READY! Opening Dashboard: {URL}")
        webbrowser.open(URL)
        print("\n--- OPERATIONAL LOGS ---")
        print("Keep this terminal open to maintain the application session.")
        print("Press CTRL+C anytime to stop all services.")
        
        # Keep the main thread alive and print logs
        while True:
            time.sleep(1)
    else:
        print("❌ UI failed to start in time. Check the logs.")
        kill_processes(None, None)

if __name__ == "__main__":
    start_services()
