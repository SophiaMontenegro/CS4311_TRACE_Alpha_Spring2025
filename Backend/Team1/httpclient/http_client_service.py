import uuid
import json
import os
from datetime import datetime
from Team1.httpclient.http_client import HTTPClient
from Team1.httpclient.proxy_server import ProxyServer

# Shared proxy and HTTP client
proxy = ProxyServer()
client = HTTPClient(proxy)

# In-memory running jobs
running_http_jobs = {}

# --- Constants ---
DATABASE_FOLDER = "Team1/database/httpclient"

# --- Service Functions ---

def generate_job_id():
    """
    Generates a unique job ID using UUID4.
    """
    return str(uuid.uuid4())

def get_project_folder(project_name: str):
    """
    Returns the sanitized folder path for a given project name.
    """
    safe_project_name = project_name.replace(" ", "_")
    return os.path.join(DATABASE_FOLDER, safe_project_name)

def get_job_filename(project_folder: str, job_id: str):
    """
    Returns the full file path for a specific job inside a project folder.
    """
    return os.path.join(project_folder, f"http_jobs_data_{job_id}.json")

def save_job_to_disk(project_name: str, job_data: dict):
    """
    Saves a single HTTP job into its own file under the project folder.
    If the project folder doesn't exist, it tries to create it.
    """
    project_folder = get_project_folder(project_name)

    try:
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
    except Exception as e:
        raise RuntimeError(f"Failed to create project folder '{project_folder}': {e}")

    filepath = get_job_filename(project_folder, job_data['job_id'])

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(job_data, f, indent=2)


def add_log_entry(job_id: str, message: str):
    """
    Adds a timestamped log entry to a running HTTP job.
    """
    timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    
    if job_id in running_http_jobs:
        running_http_jobs[job_id]['logs'].append(log_message)

def send_http_request_service(target_system: str, crafted_request: dict, project_name: str = "default_project"):
    """
    Sends an HTTP request to the target system and saves the job details.
    """
    job_id = generate_job_id()
    job_data = {
        "job_id": job_id,
        "target_system": target_system,
        "request": crafted_request,
        "response": None,
        "logs": [],
        "status": "sending",
        "created_at": datetime.now().isoformat(),
        "project_name": project_name
    }
    running_http_jobs[job_id] = job_data

    add_log_entry(job_id, f"Starting HTTP request to {target_system}")

    try:
        if not client.specify_target_system(target_system):
            raise ValueError("Invalid target system URL.")

        response = client.send_request(crafted_request)

        running_http_jobs[job_id]['response'] = response
        running_http_jobs[job_id]['status'] = "completed" if "error" not in response else "error"

        if "error" in response:
            add_log_entry(job_id, f"Error sending request: {response['error']}")
        else:
            add_log_entry(job_id, f"Request completed with status {response.get('status_code')}")

    except Exception as e:
        running_http_jobs[job_id]['status'] = "error"
        running_http_jobs[job_id]['response'] = {"error": str(e)}
        add_log_entry(job_id, f"Exception occurred: {str(e)}")
    try:
        save_job_to_disk(project_name, running_http_jobs[job_id])
    except Exception as e:
        add_log_entry(job_id, f"Failed to save job to disk: {str(e)}")
    return {
        "job_id": job_id,
        "message": "Request processed"
    }

def get_http_job(job_id: str):
    """
    Retrieves a running HTTP job by job ID.
    """
    return running_http_jobs.get(job_id)

def get_http_job_logs(job_id: str):
    """
    Retrieves logs associated with a running HTTP job.
    """
    if job_id in running_http_jobs:
        return running_http_jobs[job_id].get('logs', [])
    return []
