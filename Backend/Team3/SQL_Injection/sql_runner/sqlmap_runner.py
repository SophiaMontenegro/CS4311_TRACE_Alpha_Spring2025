import sys
import subprocess
import os
import json
from datetime import datetime
import shutil
import stat
import shlex
import threading
import platform
import signal

# Windows-specific (conditionally used)
if platform.system() == "Windows":
    import ctypes
    import win32api
    import win32con
    import win32process

HISTORY_FILE = "sqlmap_results/injection_history.json"
Program = True

# Utility for handling file permissions
def handle_remove(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Reset all saved results
def reset_service():
    resetConfirm = input("Are you sure you would like to reset (y/n): ").strip().lower()
    if resetConfirm == 'y':
        try:
            shutil.rmtree("sqlmap_results", onerror=handle_remove)
            print("[+] All previous results have been removed")
        except Exception as e:
            print(f"[-] Failed to reset: {e}")

# Show loading bar
def print_progress(percent, width=40):
    done = int(width * percent / 100)
    bar = f"[{'=' * done}{' ' * (width - done)}] {percent:.0f}%"
    print(f"\r{bar}", end='', flush=True)

# Save scan data to JSON history
def save_to_history(entry):
    os.makedirs("sqlmap_results", exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Show scan history
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
        print(f"Output    : {entry['output_folder']}/output.txt")
        print("-----------------------------")

# View output from a previous test
def view_output_file():
    if not os.path.exists(HISTORY_FILE):
        print("[-] No previous injection history found.")
        return

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    if not history:
        print("[-] No records to display.")
        return

    print("\n[+] Select a test to view its output:\n")
    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry['timestamp']} - {entry['url']}")

    try:
        selection = int(input("\nEnter the test number: ").strip())
        if 1 <= selection <= len(history):
            output_path = os.path.join(history[selection - 1]['output_folder'], "output.txt")
            if os.path.exists(output_path):
                entry = history[selection - 1]
                if "summary" in entry:
                    print(f"\n[+] Showing summarized results:\n")
                    print(entry["summary"])
                else:
                    print(f"\n[+] Showing full output from: {output_path}\n")
                    with open(output_path, "r") as f:
                        print(f.read())

            else:
                print("[-] Output file not found.")
        else:
            print("[-] Invalid selection.")
    except ValueError:
        print("[-] Invalid input.")

def extract_useful_info(output_path, summary_path):
    useful_lines = []
    keywords = [
        "[INFO] testing connection", 
        "[INFO] the back-end DBMS is",
        "[INFO] fetching", 
        "[INFO] database",
        "[INFO] table", 
        "[INFO] column", 
        "[INFO] entries",
        "[CRITICAL]", 
        "[WARNING]", 
        "[DATA]"
    ]

    with open(output_path, "r") as infile:
        for line in infile:
            if any(keyword in line for keyword in keywords):
                useful_lines.append(line.strip())

    with open(summary_path, "w") as summary_file:
        summary_file.write("\n".join(useful_lines))

    print(f"[+] Summary saved to: {summary_path}")

def extract_essential_results(output_dir):
    summary = []

    # Step 1: Try to extract injection point and DBMS info from output.txt
    output_file = os.path.join(output_dir, "output.txt")
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "parameter" in line.lower() and "injectable" in line.lower():
                    summary.append(f"[Injection Point] {line.strip()}")
                if "back-end DBMS is" in line:
                    summary.append(f"[DBMS Info] {line.strip()}")

    # Step 2: Walk through sqlmap subfolders to extract database/table dumps
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".csv"):
                parts = os.path.normpath(root).split(os.sep)
                db_name = parts[-2] if len(parts) >= 2 else "unknown_db"
                table_name = parts[-1]
                summary.append(f"\n[Dumped Data] Database: {db_name}, Table: {table_name}")
                csv_path = os.path.join(root, file)
                try:
                    with open(csv_path, "r", encoding="utf-8", errors="ignore") as csvfile:
                        rows = csvfile.readlines()
                        summary.extend([line.strip() for line in rows])
                except Exception as e:
                    summary.append(f"[!] Failed to read dump: {e}")

    if not summary:
        summary.append("[!] No significant results found.")

    return "\n".join(summary)


# Cross-platform suspend/resume
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

# Main scan logic
def run_sqlmap():
    base_url = input("Enter the target URL: ").strip()
    port = input("Enter the port: ").strip()
    params = input("Enter GET parameters (e.g. id=1&name=admin, ?id=1) or press ENTER to skip: ").strip()

    if "://" in base_url:
        protocol, rest = base_url.split("://", 1)
        if ":" not in rest:
            base_url = f"{protocol}://{rest}:{port}"
    else:
        base_url = f"http://{base_url}:{port}"

    if params:
        if "?" in base_url:
            base_url += "&" + params
        else:
            base_url += "?" + params

    print(f"\n[+] Final Target: {base_url}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("sqlmap_results", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    script_dir = os.path.dirname(__file__)
    sqlmap_path = os.path.abspath(os.path.join(script_dir, "..", "sqlmap1", "sqlmap.py"))
    python_exe = sys.executable

    cmd = [
        python_exe,
        sqlmap_path,
        "-u", base_url,
        "--batch",
        "--dump",
        "--output-dir", output_dir
    ]

    customFlag = input("Enter any additional SQLMAP flags or press ENTER to skip: ").strip()
    if customFlag:
        cmd += shlex.split(customFlag)

    print(f"[+] Running sqlmap...\n")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Real-time input handler
    def input_listener(proc):
        paused = False
        while proc.poll() is None:
            key = input("\n[Press 'p' to pause, 'r' to resume, 'q' to quit scan]: ").strip().lower()
            if key == 'p':
                print("[*] Pausing SQLMap...")
                suspend_process(proc.pid)
                paused = True
            elif key == 'r':
                print("[*] Resuming SQLMap...")
                resume_process(proc.pid)
                paused = False
            elif key == 'q':
                print("[!] Terminating SQLMap...")
                if paused:
                    print("[*] Process is paused. Resuming before termination...")
                    resume_process(proc.pid)
                    paused = False
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("[!] Process didn't terminate in time. Forcing kill.")
                    proc.kill()
                break

    threading.Thread(target=input_listener, args=(process,), daemon=True).start()

    output_file = os.path.join(output_dir, "output.txt")
    with open(output_file, "w") as f:
        for line in process.stdout:
            f.write(line)
            if "checking if the target is protected" in line.lower():
                print_progress(20)
            elif "testing connection" in line.lower():
                print_progress(40)
            elif "the back-end dbms is" in line.lower():
                print_progress(60)
            elif "fetching" in line.lower() or "dumping" in line.lower():
                print_progress(90)

        process.wait()
        print_progress(100)
        print("\n[+] Scan complete.")

    summary_path = os.path.join(output_dir, "summary.txt")
    extract_useful_info(output_file, summary_path)
   

    useful_summary = extract_essential_results(output_dir)

    save_to_history({
        "url": base_url,
        "port": port,
        "timestamp": timestamp,
        "output_folder": output_dir.replace("\\", "/"),
        "summary": useful_summary
    })

    print(f"[+] Results saved to: {output_file}")
    print(f"[+] History updated: {HISTORY_FILE}")

# CLI menu
if __name__ == "__main__":
    try:
        while Program:
            print("====== SQLMap Tool ======")
            print("1 - Perform New Injection")
            print("2 - View Previous Results")
            print("3 - Reset Services Result")
            print("4 - View Output File")
            print("5 - Quit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                run_sqlmap()
            elif choice == "2":
                view_history()
            elif choice == "3":
                reset_service()
            elif choice == "4":
                view_output_file()
            elif choice == "5":
                Program = False
                print("Goodbye")
            else:
                print("Invalid choice. Try again")
    except KeyboardInterrupt:
        print("\n[!] Exiting program...")
