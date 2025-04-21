import subprocess
import os
import time
import sys

# Get the current directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "../Frontend/"))

print(f"Starting backend from: {BACKEND_DIR}")
print(f"Starting frontend from: {FRONTEND_DIR}")

# Start backend - just execute but don't try to capture output
backend_process = subprocess.Popen(
    ["python", "main.py"], 
    cwd=BACKEND_DIR
)

# Wait a bit for backend to start
time.sleep(3)

# Start frontend
print("Starting frontend with npm run dev...")
frontend_process = subprocess.Popen(
    "npm run dev", 
    cwd=FRONTEND_DIR,
    shell=True
)

# Print info
print("\n==================================================================================================")
print("TRACE application is starting up")
print("==================================================================================================")
print("Backend API should be available at: http://127.0.0.1:8000")
print("Frontend should be available at: http://localhost:5173")
print("==================================================================================================")
print("Press Ctrl+C to stop both servers")
print("==================================================================================================\n")

# Wait for user to quit
try:
    while True:
        # Just check if processes are still running
        if backend_process.poll() is not None:
            print(f"Backend process terminated with exit code {backend_process.returncode}")
            break
        if frontend_process.poll() is not None:
            print(f"Frontend process terminated with exit code {frontend_process.returncode}")
            break
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopping all processes...")
    
    if backend_process.poll() is None:
        backend_process.terminate()
        print("Backend stopped")
    
    if frontend_process.poll() is None:
        frontend_process.terminate()
        print("Frontend stopped")
    
    print("\nGoodbye.")