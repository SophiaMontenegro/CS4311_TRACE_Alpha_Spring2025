import sys
import subprocess
import os
import json
import shutil
import stat
import shlex
import threading
import platform
import signal
import csv
from datetime import datetime
import uuid

# Windows-specific imports
if platform.system() == "Windows":
    import ctypes

# Define the results directory path - one level up from this script
RESULTS_DIR = "Team3/SQL_Injection/sqlmap_results"
HISTORY_FILE = os.path.join(RESULTS_DIR, "injection_history.json")
Program = True

# Utility to handle file permission issues
def handle_remove(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Reset service
def reset_service():
    resetConfirm = input("Are you sure you would like to reset (y/n): ").strip().lower()
    if resetConfirm == 'y':
        try:
            shutil.rmtree(RESULTS_DIR, onerror=handle_remove)
            print("[+] All previous results have been removed")
        except Exception as e:
            print(f"[-] Failed to reset: {e}")

# Progress bar
def print_progress(percent, width=40):
    done = int(width * percent / 100)
    bar = f"[{'=' * done}{' ' * (width - done)}] {percent:.0f}%"
    print(f"\r{bar}", end='', flush=True)

# Save scan history
def save_to_history(entry):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# View scan history
def view_history():
    print("\n[+] Viewing previous SQL injection test history...\n")
    if not os.path.exists(HISTORY_FILE):
        print("[-] No previous injection history found.")
        return

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    if not history:
        print("[-] No records in history.")
        return

    for i, entry in enumerate(history, 1):
        print(f"--- Test #{i} ---")
        print(f"URL       : {entry['url']}")
        print(f"Port      : {entry['port']}")
        print(f"Timestamp : {entry['timestamp']}")
        print(f"Result    : {entry['result_file']}")
        print(f"Log       : {entry['log_file']}")
        print("-----------------------------")

# Suspend process
def suspend_process(pid):
    if platform.system() == "Windows":
        try:
            PROCESS_SUSPEND_RESUME = 0x0800
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
            if not handle:
                raise Exception("Could not open process handle")
            result = ctypes.windll.ntdll.NtSuspendProcess(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
            if result != 0:
                raise Exception(f"NtSuspendProcess failed with code {result}")
        except Exception as e:
            print(f"[-] Failed to pause process: {e}")
    else:
        os.kill(pid, signal.SIGSTOP)

# Resume process
def resume_process(pid):
    if platform.system() == "Windows":
        try:
            PROCESS_SUSPEND_RESUME = 0x0800
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
            if not handle:
                raise Exception("Could not open process handle")
            result = ctypes.windll.ntdll.NtResumeProcess(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
            if result != 0:
                raise Exception(f"NtResumeProcess failed with code {result}")
        except Exception as e:
            print(f"[-] Failed to resume process: {e}")
    else:
        os.kill(pid, signal.SIGCONT)

# Run SQLMap
def run_sqlmap(base_url, port, params="", custom_flags=""):
    if "//" in base_url:
        protocol, rest = base_url.split("//", 1)
        if ":" not in rest:
            base_url = f"{protocol}//{rest}:{port}"
    else:
        base_url = f"http://{base_url}:{port}"

    if params:
        if "?" in base_url:
            base_url += "&" + params
        else:
            base_url += "?" + params

    print(f"\n[+] Final Target: {base_url}")

    # Directly save in sqlmap_results folder
    os.makedirs(RESULTS_DIR, exist_ok=True)

    #existing = [int(name.replace("sql_results_", "").replace(".csv", "")) for name in os.listdir(RESULTS_DIR) if name.startswith("sql_results_")]
    #next_job_id = max(existing, default=6999) + 1
    next_job_id = str(uuid.uuid4())

    result_filename = f"sql_results_{next_job_id}.csv"
    log_filename = f"sql_log_{next_job_id}.csv"

    result_path = os.path.join(RESULTS_DIR, result_filename)
    log_path = os.path.join(RESULTS_DIR, log_filename)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    script_dir = os.path.dirname(__file__)
    sqlmap_path = os.path.abspath(os.path.join(script_dir, "..", "sqlmap1", "sqlmap.py"))
    python_exe = sys.executable

    cmd = [
        python_exe, sqlmap_path,
        "-u", base_url,
        "--batch",
        "--dump"
    ]

    if custom_flags:
        cmd += shlex.split(custom_flags)

    print(f"[+] Running sqlmap...\n")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Create an event to signal thread termination
    stop_event = threading.Event()
    
    # Live input listener thread with non-blocking input
    def input_listener(proc, stop_event):
        paused = False
        import select
        import sys
        import time
        
        # Only use this when running in CLI mode, not when called via API
        if not sys.__stdin__.isatty():
            return
            
        while proc.poll() is None and not stop_event.is_set():
            # Non-blocking approach to check for input
            print("\r[Press 'p' to pause, 'r' to resume, 'q' to quit scan]", end='', flush=True)
            time.sleep(1)  # Check periodically instead of blocking
            
            # Only process input if there's something to read
            if select.select([sys.stdin], [], [], 0.0)[0]:
                key = sys.stdin.readline().strip().lower()
                if key == 'p':
                    suspend_process(proc.pid)
                    print("[*] SQLMap Paused.")
                    paused = True
                elif key == 'r':
                    resume_process(proc.pid)
                    print("[*] SQLMap Resumed.")
                    paused = False
                elif key == 'q':
                    if paused:
                        resume_process(proc.pid)
                    print("[!] Terminating SQLMap...")
                    proc.terminate()
                    break

    # Start the listener thread
    listener_thread = threading.Thread(target=input_listener, args=(process, stop_event), daemon=True)
    listener_thread.start()

    try:
        with open(result_path, "w", encoding="utf-8", newline='') as result_file, open(log_path, "w", encoding="utf-8", newline='') as log_file:
            csv_writer = csv.writer(result_file)
            csv_writer.writerow(["Type", "Details"])

            for line in process.stdout:
                log_file.write(line)
                lower_line = line.lower()

                if "checking if the target is protected" in lower_line:
                    print_progress(20)
                elif "testing connection" in lower_line:
                    print_progress(40)
                elif "the back-end dbms is" in lower_line:
                    print_progress(60)
                elif "fetching" in lower_line or "dumping" in lower_line:
                    print_progress(90)

                important_keywords = ["parameter:", "type:", "title:", "payload:", "database:", "table:", "column:", "data:"]
                if any(keyword in lower_line for keyword in important_keywords):
                    clean_line = line.strip()
                    for keyword in important_keywords:
                        if keyword in lower_line:
                            csv_writer.writerow([keyword.replace(":", "").capitalize(), clean_line])
                            break

        process.wait()
        print_progress(100)
        print("\n[+] Scan complete.")
        
    finally:
        # Signal the listener thread to stop
        stop_event.set()
        
        # Make sure SQLMap process is terminated
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
        # No need to join daemon thread, but it's good practice
        if listener_thread.is_alive():
            try:
                listener_thread.join(timeout=1)
            except:
                pass

    save_to_history({
        "url": base_url,
        "port": port,
        "timestamp": timestamp,
        "result_file": result_path.replace("\\", "/"),
        "log_file": log_path.replace("\\", "/")
    })

    print(f"[+] Results saved to: {result_path}")
    print(f"[+] Log saved to: {log_path}")
    print(f"[+] History updated: {HISTORY_FILE}")

    return {
        "job_id": next_job_id,
        "result_file": result_path,
        "log_file": log_path
    }

# Main function to handle API requests
def handle_sqlmap_request(data):
    base_url = data.get("target_url")
    port = data.get("port")
    params = data.get("injectable_params", "")
    custom_flags = data.get("custom_flags", "")

    if not base_url or not port:
        return {"error": "Missing required parameters"}

    result = run_sqlmap(base_url, port, params, custom_flags)
    return result

# Remove or comment out the CLI menu
# if __name__ == "__main__":
#     try:
#         while Program:
#             print("====== SQLMap Tool ======")
#             print("1 - Perform New Injection")
#             print("2 - View Previous Results")
#             print("3 - Reset Service Results")
#             print("4 - Quit")

#             choice = input("Choose an option: ").strip()

#             if choice == "1":
#                 run_sqlmap()
#             elif choice == "2":
#                 view_history()
#             elif choice == "3":
#                 reset_service()
#             elif choice == "4":
#                 Program = False
#                 print("Goodbye!")
#             else:
#                 print("Invalid choice. Try again")
#     except KeyboardInterrupt:
#         print("\n[!] Exiting program...")

# Add this at the end of the file
if __name__ == "__main__":
    # This can be used for testing or standalone execution
    print("SQLMap Runner is ready to be called via API")
