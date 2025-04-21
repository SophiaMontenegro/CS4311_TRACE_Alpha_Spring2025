import logging
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import os
import json
import time
import random

from Team7.src.modules.dbf.dbf_manager import DirectoryBruteForceManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track the different jobs
running_jobs = {}
# Format: {job_id: {status, created_at, config, progress, urls_processed, total_urls, logs_ taks, dbf_instance}}
job_results = {}
# Format: {job_id: {status, results_file, urls_processed, complated_at, logs}}
active_connections = {}
# Format: {job_id: {websocket1, websocket2, ...}}

# Dictionary to keep track of dbf instances
dbf_instances: Dict[str, Any] = {}

# Pydantic models
class DBFConfig(BaseModel):
    """
    Configuration model for DBF jobs
    """
    target_url: str
    wordlist: List[str]
    top_dir: Optional[str] = ''
    hide_status: Optional[List[int]] = None
    show_only_status: Optional[List[int]] = None
    length_filter: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    attempt_limit: Optional[int] = -1

    # Handles any formatted issues with from the frontend
    class Config:
        alias_generator = lambda field_name: field_name.replace('_', '-')
        populate_by_name = True

    # Log the received data from frontend
    def debug_request(cls, data: dict):
        logger.info(f'Raw request data: {data}')
        for key, value in data.items():
            logger.info(f'Field: {key}, Value: {value}, Type: {type(value)}')
        return data
    
class DBFJobResponse(BaseModel):
    """Response model for DBF job status"""
    job_id: str
    message: str
    status: str
    progress: Optional[float] = 0
    processed_requests: Optional[int] = 0
    filtered_requests: Optional[int] = 0
    requests_per_second: Optional[float] = 0

class DBFResultItem(BaseModel):
    """
    Model for a single DBF result item.
    """
    id: int
    url: str
    status: int
    payload: str
    length: int
    error: bool

class DBFResults(BaseModel):
    """
    Model for the completed DBF results
    """
    results: List[DBFResultItem]

class DBFProgressTracker:
    """
    Tracks progress of a DBF job and broadcasts updates through the websockets
    """
    def __init__(self, job_id):
        self.job_id = job_id
        self.processed_count = 0
        self.filtered_count = 0
        self.total_count = 0
        self.logs = []

    def add_log(self, message):
        """
        Add a log message and broadcast it to the connected clients
        """
        timestamp = datetime.now().isoformat()
        log_entry = f'[{timestamp}] {message}'
        self.logs.append(log_entry)

        # Update the logs in running_jobs 
        if self.job_id in running_jobs:
            running_jobs[self.job_id]['logs'] = self.logs.copy()
        logger.info(f'Job {self.job_id}: {message}')

        # Broadcast the log message to the connected websockets
        self.broadcast_message('log', {'message': log_entry})

    def update_progress_from_callback(self, processed, total, current_payload=None, error=None):
        """
        Update job progress metrics and broadcast to clients - called from the DBF manager callback
        """
        self.processed_count = processed
        
        if self.job_id in running_jobs and 'last_row' in running_jobs[self.job_id]:
            last_row = running_jobs[self.job_id]['last_row']
            self.broadcast_message('new_row', {'row': last_row})

        # Update the job status of the current running job
        if self.job_id in running_jobs:
            if 'progress_start_time' not in running_jobs[self.job_id]:
                running_jobs[self.job_id]['progress_start_time'] = time.time()
                running_jobs[self.job_id]['progress_duration'] = random.uniform(5.0, 15.0)

            # Calcualte progress based on elapsed time
            start_time = running_jobs[self.job_id]['progress_start_time']
            duration = running_jobs[self.job_id]['progress_duration']
            elapsed = time.time() - start_time

            # Calculate a percentage based on the elapsed time, > 99
            if elapsed >= duration:
                progress = 99
            else:
                progress = min(int((elapsed / duration) * 99), 99)

            # Calcualte requests per second
            try:
                rps = self.processed_count / elapsed if elapsed > 0 else 0
            except Exception:
                rps = 0
            
            # Update the metrics in running_jobs
            running_jobs[self.job_id].update({
                'processed_requests': self.processed_count,
                'filtered_requests': self.filtered_count,
                'progress': progress,
                'requests_per_second': rps
            })

            # Broadcast progress update to the connected websockets
            self.broadcast_message('progress', {
                'processed_requests': self.processed_count,
                'filtered_requests': self.filtered_count,
                'progress': progress,
                'requests_per_second': rps,
                'current_payload': current_payload
            })
        
        # Log the progress
        if error:
            self.add_log(f'Error processing {current_payload}: {error}')
        elif current_payload:
            self.add_log(f'Processed: {self.processed_count}/{total}, Current: {current_payload}')
                
    def set_status(self, status):
        """
        Set job status and broadcast to connected clients.
        """
        if self.job_id in running_jobs:
            running_jobs[self.job_id]['status'] = status
            self.add_log(f'Job status changed to: {status}')

            self.broadcast_message('status', {'status': status})

    def broadcast_message(self, message_type, data):
        """
        Broadcast a message to all the connected clients through the websockets.
        """
        message = {
            'type': message_type,
            'job_id': self.job_id,
            'data': data
        }

        # Send it to all the connected clients
        if self.job_id in active_connections:
            for websocket in active_connections[self.job_id]:
                asyncio.create_task(websocket.send_json(message))

    def handle_new_result(self, result):
        """
        Handle a new result from the DBF scan
        """
        self.broadcast_message('new_row', {'row': result})
        self.filtered_count = len(result) if isinstance(result, list) else self.filtered_count + 1

async def run_dbf_task(job_id: str, config: DBFConfig):
    """
    Run a DBF job asynchronously and update state.
    """
    tracker = DBFProgressTracker(job_id)
    tracker.add_log(f'Starting DBF job with config: {config.model_dump()}')
    tracker.total_count = len(config.wordlist)

    try:
        tracker.set_status('running')
        running_jobs[job_id]['started_at'] = datetime.now().isoformat()

        # Initialize the DBF Manager instance
        dbf_manager = DirectoryBruteForceManager()
        dbf_instances[job_id] = dbf_manager

        # Attach the row broadcast callback
        def handle_new_row(row):
            logger.info(f'[Backend] Broadcasting new row for {job_id}: {row["url"]}')
            tracker.broadcast_message('new_row', {'row': row})
        dbf_manager.on_new_row = handle_new_row

        # Attach the progress callback
        def progress_callback(processed, total, current_payload=None, error=None):
            if job_id in running_jobs:
                job_status = running_jobs[job_id].get('status', '')
                if job_status == 'stopped':
                    dbf_manager.stop()
                    raise asyncio.CancelledError('Job stopped by user')
                elif job_status == 'paused':
                    dbf_manager.pause()
                    asyncio.create_task(wait_for_resume(job_id, dbf_manager))
            
            metrics = dbf_manager.get_metrics()
            tracker.filtered_count = metrics['filtered_requests']
            
            tracker.update_progress_from_callback(processed, total, current_payload, error)
            
        dbf_manager.progress_callback = progress_callback

        # Configure the DBF manager
        tracker.add_log('Configuring Directory Brute Force Scan')
        dbf_manager.configure_scan(
            target_url=config.target_url,
            wordlist=config.wordlist,
            top_dir=config.top_dir or '',
            hide_status=config.hide_status or [],
            show_only_status=config.show_only_status or [],
            length_filter=config.length_filter,
            headers=config.headers or {},
            attempt_limit=config.attempt_limit or -1
        )

        # Start the scan
        tracker.add_log('Starting Directory Brute Force scan.')
        await dbf_manager.start_scan()

        # Get the final metrics
        metrics = dbf_manager.get_metrics()

        # Get filtered results
        results = dbf_manager.get_filtered_results()

        results_file = f'Team7/src/database/dbf/dbf_results_{job_id}.json'
        with open(results_file, 'w') as file:
            json.dump(results, file)

        tracker.add_log(f'Scan completed. Found {len(results)} matching paths.')

        # Update job status
        job_results[job_id] = {
            'status': 'completed',
            'results_file': results_file,
            'processed_requests': metrics['processed_requests'],
            'filtered_requests': metrics['filtered_requests'],
            'requests_per_second': metrics['requests_per_second'],
            'running_time': metrics['running_time'],
            'completed_at': datetime.now().isoformat(),
            'logs': tracker.logs
        }

        # Broadcast completion message
        tracker.broadcast_message('completed', {
            'processed_requests': metrics['processed_requests'],
            'filtered_requests': metrics['filtered_requests'],
            'progress': 100,
            'message': 'Directory Brute Force scan completed successfully.'
        })

        # Remove the instance
        if job_id in dbf_instances:
            del dbf_instances[job_id]
        if job_id in running_jobs:
            del running_jobs[job_id]

        tracker.add_log(f'Job {job_id} completed successfully.')

    # Handle cancellation
    except asyncio.CancelledError:
        tracker.add_log('Job cancelled by user.')

        job_results[job_id] = {
            'status': 'stopped',
            'processed_requests': tracker.processed_count,
            'filtered_requests': tracker.filtered_count,
            'completed_at': datetime.now().isoformat(),
            'logs': tracker.logs
        }

        if job_id in dbf_instances:
            del dbf_instances[job_id]
        if job_id in running_jobs:
            del running_jobs[job_id]

    except Exception as e:
        error_message = f'Error DBF job: {str(e)}'
        logger.error(f'Error in DBF job {job_id}: {e}')
        tracker.add_log(error_message)

        # Broadcast the error message
        tracker.broadcast_message('error', {
            'message': error_message,
        })

        # Update the job status
        if job_id in running_jobs:
            running_jobs[job_id]['status'] = 'error'
            running_jobs[job_id]['error'] = error_message

            job_results[job_id] = {
                'status': 'error',
                'error': error_message,
                'processed_requests': tracker.processed_count,
                'filtered_requests': tracker.filtered_count,
                'completed_at': datetime.now().isoformat(),
                'logs': tracker.logs
            }

            if job_id in dbf_instances:
                del dbf_instances[job_id]
            if job_id in running_jobs:
                del running_jobs[job_id]

async def wait_for_resume(job_id: str, dbf_manager: DirectoryBruteForceManager):
    """
    Wait for job status to change from paused 
    """
    while job_id in running_jobs and running_jobs[job_id].get('status') == 'paused':
        await asyncio.sleep(0.5)

    if job_id in running_jobs and running_jobs[job_id].get('status') == 'stopped':
        dbf_manager.stop()
        raise asyncio.CancelledError('Job stopped while paused.')

    dbf_manager.resume()

def get_job_status_message(job_id: str) -> Dict[str, Any]:
    """
    Generate a status message for a job based on its current state.
    """
    if job_id in running_jobs:
        job = running_jobs[job_id]
        return {
            'type': 'status',
            'job_id': job_id,
            'data': {
                'status': job.get('status', 'unknown'),
                'progress': job.get('progress', 0),
                'processed_requests': job.get('processed_requests', 0),
                'filtered_requests': job.get('filtered_requests', 0),
                'requests_per_second': job.get('requests_per_second', 0),
                'created_at': job.get('created_at', ''),
                'started_at': job.get('started_at', '')
            }
        }
    elif job_id in job_results:
        job = job_results[job_id]
        return {
            'type': 'status',
            'job_id': job_id,
            'data': {
                'status': job.get('status', 'completed'),
                'progress': 100 if job.get('status') == 'completed' else 0,
                'processed_requests': job.get('processed_requests', 0),
                'filtered_requests': job.get('filtered_requests', 0),
                'requests_per_second': job.get('requests_per_second', 0),
                'completed_at': job.get('completed_at', ''),
                'error': job.get('error', None)
            }
        }
    else:
        return {
            'type': 'error',
            'job_id': job_id,
            'data': {'message': f'Job {job_id} not found'}
        }
    
def get_job_logs(job_id: str) -> List[str]:
    """
    Retrieve logs for a specific job.
    """
    if job_id in running_jobs and 'logs' in running_jobs[job_id]:
        return running_jobs[job_id]['logs']
    elif job_id in job_results and 'logs' in job_results[job_id]:
        return job_results[job_id]['logs']
    return []