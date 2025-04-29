import logging
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import asyncio
import os
import json
from fastapi import HTTPException

from Team7.src.modules.ai.credential_generator import Credential_Generator
from Team7.src.modules.ai.nlp import NLP
from Team7.src.modules.ai.web_scraper import WebScraper

# set up the logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track the different Jobs
running_jobs = {}
# Format: {job_id: {status, created_at, config, progress, urls_processed, total_urls, logs, task}}
job_results = {}
# Format: {job_id: {status, results_file, completed_at, logs}}
active_connections = {}
# Format: {job_id: [websocket1, websocket2,...]}

# Pydantic models
class MLConfig(BaseModel):
    """
    Configuration model for ML jobs
    """
    credential_count: Optional[int] = 10
    wordlist: Optional[str] = None
    min_username_length: Optional[int] = 12
    username_caps: Optional[bool] = True
    username_numbers: Optional[bool] = True
    username_symbols: Optional[bool] = True
    min_password_length: Optional[int] = 12
    password_caps: Optional[bool] = True
    password_numbers: Optional[bool] = True
    password_symbols: Optional[bool] = True

    class Config:
        alias_generator = lambda field_name: field_name.replace("_", "-")
        populate_by_name = True


class MLJobResponse(BaseModel):
    """
    Response model for ML job status.
    """
    job_id: str
    message: str
    status: str
    progress: Optional[float] = 0
    step: Optional[str] = "initializing"
    total_steps: int = 3  # WebScraper -> NLP -> Credential_Generator


class CredentialItem(BaseModel):
    """
    Model for a single credential item.
    """
    id: int
    username: str
    username_score: float
    password: str
    is_secure: bool
    password_evaluation: str


class CredentialResults(BaseModel):
    """
    Model for the completed credential results
    """
    results: List[CredentialItem]


class MLProgressTracker:
    """
    Tracks progress of an ML job and broadcasts updates
    """
    def __init__(self, job_id):
        self.job_id = job_id
        self.total_processed = 0
        self.logs = []
        self.current_step = "initializing"
        self.steps = ["web_scraping", "nlp_processing", "credential_generation"]
        self.step_index = -1

    def add_log(self, message):
        """Add a log message and broadcast it to connected clients"""
        timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)

        # Update the logs in running_jobs
        if self.job_id in running_jobs:
            running_jobs[self.job_id]["logs"] = self.logs.copy()
        logger.info(f"ML Job {self.job_id}: {message}")

        # Broadcast the log message to the connected websockets
        self._broadcast_message("log", {"message": log_entry})

    def next_step(self):
        """Move to the next step in the ML pipeline"""
        self.step_index += 1
        if int(self.step_index) < int(len(self.steps)):
            self.current_step = self.steps[self.step_index]
            progress = (self.step_index + 1) / len(self.steps) * 100

            # Update the job status
            if self.job_id in running_jobs:
                running_jobs[self.job_id].update(
                    {"progress": progress, "step": self.current_step}
                )

            # Broadcast the step update
            self._broadcast_message(
                "progress",
                {
                    "progress": progress,
                    "step": self.current_step,
                    "step_index": self.step_index,
                    "total_steps": len(self.steps),
                },
            )

            self.add_log(f"Starting step: {self.current_step}")
            return self.current_step
        return None

    def set_status(self, status):
        """Set job status and broadcast to connected clients"""
        if self.job_id in running_jobs:
            running_jobs[self.job_id]["status"] = status
            self.add_log(f"Job status changed to: {status}")

            # Broadcast the status update
            self._broadcast_message("status", {"status": status})

    def _broadcast_message(self, message_type, data):
        """Broadcast a message to all connected clients through websockets"""
        message = {"type": message_type, "job_id": self.job_id, "data": data}

        # Send to all clients
        if self.job_id in active_connections:
            for websocket in active_connections[self.job_id]:
                asyncio.create_task(websocket.send_json(message))


async def run_ml_task(job_id: str, config: MLConfig):
    """
    Run an ML job asynchronously and update state.
    """
    tracker = MLProgressTracker(job_id)
    tracker.add_log(f"Starting ML job with config: {config.model_dump()}")

    csv_file = None
    credentials = []

    try:
        # Update job status
        tracker.set_status("running")
        running_jobs[job_id]["started_at"] = datetime.now().isoformat()

        # Step 1: Web Scraping
        step = tracker.next_step()
        tracker.add_log("Starting web scraping")

        database_path = "Team7/src/database/raw_html"
        scraper = WebScraper(folder_path=database_path)
        csv_file = await scraper.scrape_pages()

        if not csv_file:
            raise ValueError("Web scraping failed to produce a CSV file")

        tracker.add_log(f"Web scraping completed, saved to {csv_file}")

        # Step 2: NLP Processing
        step = tracker.next_step()
        tracker.add_log("Starting NLP processing")

        nlp = NLP()
        nlp.subroutine(csv_file)

        tracker.add_log("NLP processing completed")

        # Step 3: Credential Generation
        step = tracker.next_step()
        tracker.add_log("Starting credential generation")

        if config.wordlist:
            wordlist_path = f"Team7/src/database/ai/temp_wordlist_{job_id}.txt"
            wordlist_lines = config.wordlist.strip().splitlines()
            with open(wordlist_path, "w") as f:
                for word in wordlist_lines:
                    f.write(f"{word.strip()}\n")
        else:
            raise ValueError("No wordlist provided")

        cred_gen = Credential_Generator(
            csv_path=csv_file,
            wordlist_path=wordlist_path,
            min_username_length=config.min_username_length,
            username_caps=config.username_caps,
            username_numbers=config.username_numbers,
            username_special_chars=config.username_symbols,
            min_password_length=config.min_password_length,
            password_caps=config.password_caps,
            password_numbers=config.password_numbers,
            password_special_chars=config.password_symbols,
        )
        if config.min_username_length:
            cred_gen.min_username_length = config.min_username_length
        if config.min_password_length:
            cred_gen.min_password_length = config.min_password_length

        # Ensure credential_count is an integer
        credential_count = config.credential_count
        if not isinstance(credential_count, int):
            credential_count = int(credential_count)

        credentials = cred_gen.generate_credentials(count=credential_count)

        # Process the credentials
        cred_gen.process_ai_wordlist(credentials)

        # Save results to a JSON file for API access
        results_file = f"Team7/src/database/ai/ml_credentials_{job_id}.json"

        # Convert credentials to a list of dictionaries
        credential_dicts = []
        for i, (username, password) in enumerate(credentials):
            username_score = cred_gen.calculate_username_strength(username)
            password_response = cred_gen.calculate_password_strength(password)
            is_secure = "secure" in password_response.lower()

            credential_dicts.append(
                {
                    "id": i,
                    "username": username,
                    "username_score": username_score,
                    "password": password,
                    "is_secure": is_secure,
                    "password_evaluation": password_response,
                }
            )

        # Save to JSON file
        with open(results_file, "w") as f:
            json.dump(credential_dicts, f, indent=2)

        tracker.add_log(f"Credential generation completed, saved to {results_file}")

        # Update job status
        job_results[job_id] = {
            "status": "completed",
            "results_file": results_file,
            "completed_at": datetime.now().isoformat(),
            "logs": tracker.logs.copy(),
        }

        # Broadcast completion message
        await asyncio.sleep(1)  # short pause to ensure frontend is in ready state
        tracker._broadcast_message(
            "completed",
            {
                "progress": 100,
                "message": "ML job completed successfully",
                "credentials_count": len(credentials),
            },
        )

        # Remove from running jobs
        running_jobs[job_id]["status"] = "completed"
        await asyncio.sleep(10)
        if job_id in running_jobs:
            del running_jobs[job_id]

        tracker.add_log(f"Job {job_id} completed successfully")

    except Exception as e:
        error_message = f"Error in ML job: {str(e)}"
        logger.error(f"Error in ML job {job_id}: {e}")
        tracker.add_log(error_message)

        # Broadcast the error message
        tracker._broadcast_message(
            "error",
            {
                "message": error_message,
            },
        )

        # Update job status to error
        if job_id in running_jobs:
            running_jobs[job_id]["status"] = "error"
            running_jobs[job_id]["error"] = error_message

            # Move to job_results
            job_results[job_id] = {
                "status": "error",
                "error": error_message,
                "completed_at": datetime.now().isoformat(),
                "logs": tracker.logs.copy(),
            }

            # Remove from running jobs
            del running_jobs[job_id]


def get_job_status_message(job_id: str) -> Dict[str, Any]:
    """
    Generate a status message for a job based on its current state.
    """
    if job_id in running_jobs:
        job = running_jobs[job_id]
        return {
            "type": "status",
            "job_id": job_id,
            "data": {
                "status": job.get("status", "unknown"),
                "progress": job.get("progress", 0),
                "step": job.get("step", "initializing"),
                "created_at": job.get("created_at", ""),
                "started_at": job.get("started_at", ""),
            },
        }
    elif job_id in job_results:
        job = job_results[job_id]
        return {
            "type": "status",
            "job_id": job_id,
            "data": {
                "status": job.get("status", "completed"),
                "progress": 100,
                "completed_at": job.get("completed_at", ""),
                "error": job.get("error", None),
            },
        }
    else:
        return {
            "type": "error",
            "job_id": job_id,
            "data": {"message": f"Job {job_id} not found"},
        }


def get_job_logs(job_id: str) -> List[str]:
    """
    Retrieve logs for a specific job.
    """
    logger.info(f"Getting logs for ML job: {job_id}")
    if job_id in running_jobs and "logs" in running_jobs[job_id]:
        logger.info(
            f"Found {len(running_jobs[job_id]['logs'])} logs in running job {job_id}"
        )
        return running_jobs[job_id]["logs"]
    elif job_id in job_results and "logs" in job_results[job_id]:
        logger.info(
            f"Found {len(job_results[job_id]['logs'])} logs in completed job {job_id}"
        )
        return job_results[job_id]["logs"]
    logger.warning(f"No logs found for ML job {job_id}")
    return []
