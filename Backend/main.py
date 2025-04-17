import subprocess
import os
import time

# --- Paths ---
FRONTEND_DIR = os.path.abspath("../Frontend/")
BACKEND_CMD = ["uvicorn", "main_api:app", "--reload"]
FRONTEND_CMD = ["npm", "run", "dev"]

# --- Start Backend ---
backend_process = subprocess.Popen(BACKEND_CMD)

# --- Wait a bit before frontend ---
time.sleep(2)  # short delay to ensure backend starts

# --- Start Frontend ---
frontend_process = subprocess.Popen(FRONTEND_CMD, cwd=FRONTEND_DIR)

# --- Wait for user to quit ---
try:
    print("Both processes are running. Press Ctrl+C to stop.")
    backend_process.wait()
    frontend_process.wait()
except KeyboardInterrupt:
    print("\nStopping processes...")
    backend_process.terminate()
    frontend_process.terminate()
