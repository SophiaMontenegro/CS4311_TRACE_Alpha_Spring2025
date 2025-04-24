import logging
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import os
import json
import time
import random

from Team7.src.modules.fuzzer.fuzzer_manager import FuzzerManager

# set up the logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track the different Jobs
running_jobs = {}
# Format: {job_id: {status, created_at, config, progress, urls_processed, total_urls, logs, task, fuzzer_instance}}
job_results = {}
# Format: {job_id, {status, result_file, urls_processed, completed_at, logs}}
active_connections = {}
# Format: {job_id: {websocket1, websocket2,...}}

# Dictionary to keep track of fuzzer instances
fuzzer_instances: Dict[str, Any] = {}

# Pydantic models
class FuzzerConfig(BaseModel):
    """
    Configuration model for fuzzer jobs
    """
    target_url: str
    http_method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    body_template: Optional[Dict[str, str]] = None
    parameters: List[str]
    payloads: Optional[List[str]] = None
    payload_file: Optional[str] = None
    hide_status: Optional[List[int]] = None
    show_status: Optional[List[int]] = None
    filter_content_length: Optional[List[int]] = None

    # Handles any formatted issues from the frontend
    class Config:
        alias_generator = lambda field_name: field_name.replace('_', '-')
        populate_by_name = True

    # Log the received data from frontend
    def debug_request(cls, data: dict):
        logger.info(f'Raw request data: {data}')
        for key, value in data.items():
            logger.info(f'Field: {key}, Value: {value}, Type: {type(value)}')
        return data
    
class FuzzerJobResponse(BaseModel):
    """
    Response model for fuzzer job status.
    """
    job_id: str
    message: str
    status: str
    progress: Optional[float] = 0
    urls_processed: Optional[int] = 0
    total_urls: Optional[int] = 0

class FuzzerResultItem(BaseModel):
    """
    Model for a single fuzzer result item.
    """
    id: int
    response: int  # HTTP status code
    lines: int
    words: int
    chars: int
    payload: str
    length: int
    error: bool

class FuzzerResults(BaseModel):
    """
    Model for the completed fuzzer results
    """
    results: List[FuzzerResultItem]

class FuzzerProgressTracker:
    """
    Tracks progress of a fuzzer job and broadcasts updates through the websockets
    """
    def __init__(self, job_id):
        self.job_id = job_id
        self.processed_requests = 0
        self.logs = []

    def add_log(self, message):
        """
        Add a log message and broadcast it to connected clients
        """
        timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
        log_entry = f'[{timestamp}] {message}'
        self.logs.append(log_entry)

        # Update the logs in running_jobs
        if self.job_id in running_jobs:
            running_jobs[self.job_id]['logs'] = self.logs
        logger.info(f'Job {self.job_id}: {message}')

        # Broadcast the log message to the other connected  websockets
        self._broadcast_message('log', {'message': log_entry})

    def update_progress(self, request_count, total_requests, current_payload=None, error=None):
        self.processed_requests = request_count

        # Optional: Send incremental result rows
        if self.job_id in running_jobs and 'last_row' in running_jobs[self.job_id]:
            last_row = running_jobs[self.job_id]['last_row']
            self._broadcast_message('new_row', {'row': last_row})

        # Update the job status of the current running job
        if self.job_id in running_jobs:
            limit = total_requests or running_jobs[self.job_id].get('total_urls', 100)
            
            if 'progress_start_time' not in running_jobs[self.job_id]:
                running_jobs[self.job_id]['progress_start_time'] = time.time()
                running_jobs[self.job_id]['progress_duration'] = random.uniform(5.0, 10.0)
            
            start_time = running_jobs[self.job_id]['progress_start_time']
            duration = running_jobs[self.job_id]['progress_duration']
            elapsed = time.time() - start_time
            
            if elapsed >= duration:
                progress = 99 
            else:
                progress = min(int((elapsed / duration) * 99), 99)
            
            running_jobs[self.job_id].update({
                'urls_processed': self.processed_requests,
                'progress': progress
            })

            # Broadcast progress update to the connected websockets
            self._broadcast_message('progress', {
                'processed_requests': self.processed_requests,
                'progress': progress,
                'total_requests': limit,
                'current_payload': current_payload
            })

        if error:
            self.add_log(f'Error processing request: {error}')
        elif current_payload:
            self.add_log(f'Processing payload: {current_payload}')

    def set_status(self, status):
        """
        Set job status and broadcast to connected clients.
        """
        if self.job_id in running_jobs:
            running_jobs[self.job_id]['status'] = status
            self.add_log(f'Job status changed to: {status}')

            # Broadcast the status update to the connected websockets
            self._broadcast_message('status', {'status': status})

    def _broadcast_message(self, message_type, data):
        """
        Broadcast a message to all the connected clients throught the websockets.
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

async def run_fuzzer_task(job_id: str, config: FuzzerConfig):
    """
    Run a fuzzer job asynchronously and update state.
    """
    tracker = FuzzerProgressTracker(job_id)
    tracker.add_log(f'Starting fuzzer job with config: {config.model_dump()}')

    try:
        tracker.set_status('running')
        running_jobs[job_id]['started_at'] = datetime.now().isoformat()

        # Initialize fuzzer manager
        fuzzer = FuzzerManager()

        # Store the fuzzer instance so can pause/stop it
        fuzzer_instances[job_id] = fuzzer

        def handle_new_row(row):
            print(f'[Backend] Broadcasting new row for {job_id}: {row['payload']}')
            tracker._broadcast_message('new_row', {'row': row})
        fuzzer.on_new_row = handle_new_row

        # Prepare the payloads
        payloads = config.payloads or []
        if config.payload_file and os.path.exists(config.payload_file):
            with open(config.payload_file, 'r', encoding='utf-8') as f:
                file_payloads = [line.strip() for line in f if line.strip()]
                payloads.extend(file_payloads)

        # Use default payloads if onhe isn't provided
        if not payloads:
            payloads = ['test', 'admin', 'password', '1234', '<script>alert(1)</script>']

        # Calcualte total requests for progress tracking
        total_requests = len(payloads) * len(config.parameters)
        running_jobs[job_id]['total_urls'] = total_requests

        # Configure the fuzzer
        tracker.add_log('Configuring fuzzer')

        # Set up filter criteria based on config
        if config.hide_status:
            fuzzer.response_processor.set_filters(
                status_filter=[],
                hide_codes=config.hide_status
            )
        elif config.show_status:
            fuzzer.response_processor.set_filters(
                status_filter=config.show_status,
                hide_codes=[]
            )

        fuzzer.configure_fuzzing(
            target_url=config.target_url,
            http_method=config.http_method,
            headers=config.headers or {},
            cookies=config.cookies or {},
            proxy=config.proxy,
            body_template=config.body_template or {},
            parameters=config.parameters,
            payloads=payloads
        )

        tracker.add_log('Fuzzer configured successfully')

        # Progress Update
        def progress_callback(request_count, total_count, current_payload=None, error=None):
            if job_id in running_jobs:
                job_status = running_jobs[job_id].get('status', '')
                if job_status == 'stopped':
                    fuzzer.stop()
                    raise asyncio.CancelledError('Job stopped by user.')
                elif job_status == 'paused':
                    fuzzer.pause()
                    asyncio.create_task(wait_for_resume(job_id, fuzzer))
            tracker.update_progress(request_count, total_count, current_payload, error)
        fuzzer.progress_callback = progress_callback

        # Start fuzing
        tracker.add_log('Starting fuzzer')
        await fuzzer.start_fuzzing()
        tracker.add_log('Fuzzer execution completed')

        metrics = fuzzer.get_metrics()
        results = fuzzer.get_filtered_results()

        formatted_results = []
        for idx, result in enumerate(results):
            formatted_results.append({
                'id': idx+1,
                'response': result.get('response', 0),
                'lines': len(result.get('snippet', '').splitlines()),
                'words': len(result.get('snippet', '').split()),
                'chars': len(result.get('snippet', '')),
                'payload': result.get('payload', ''),
                'length': result.get('length', 0),
                'error': result.get('error', False)
            })

        # Save the results
        results_file = f'Team7/src/database/fuzzer/Fuzzer_results_{job_id}.json' 
        with open(results_file, 'w') as file:
            json.dump(formatted_results, file)
        
        tracker.add_log(f'Results saved to {results_file}')

        # Update the job status after completed
        job_results[job_id] = {
            'status': 'completed',
            'results_file': results_file,
            'urls_processed': fuzzer.request_count,
            'completed_at': datetime.now().isoformat(),
            'total_urls': total_requests,
            'logs': tracker.logs,
            'metrics': metrics
        }

        # Broadcast the completed status
        tracker._broadcast_message('completed', {
            'processed_requests': fuzzer.request_count,
            'total_requests': total_requests,
            'progress': 100,
            'message': 'Fuzzer job completed successfully'
        })

        # Clean up
        if job_id in fuzzer_instances:
            del fuzzer_instances[job_id]
        if job_id in running_jobs:
            del running_jobs[job_id]

        tracker.add_log(f'Job {job_id} completed without errors.')

    # Handle job stopping
    except asyncio.CancelledError:
        tracker.add_log('Job cancelled by user')

        job_results[job_id] = {
            'status': 'stopped',
            'urls_processed': tracker.processed_requests,
            'completed_at': datetime.now().isoformat(),
            'logs': tracker.logs
        }

        if job_id in fuzzer_instances:
            del fuzzer_instances[job_id]
        if job_id in running_jobs:
            del running_jobs[job_id]
    
    except Exception as e:
        error_message = f'Error in fuzzer job: {str(e)}'
        logger.error(f'Error in fuzzer job {job_id}: {e}')
        tracker.add_log(error_message)

        tracker._broadcast_message('error', {
            'message': error_message
        })

        # Update the status
        if job_id in running_jobs:
            running_jobs[job_id]['status'] = 'error'
            running_jobs[job_id]['error'] = error_message

            job_results[job_id] = {
                'status': 'error',
                'error': error_message,
                'urls_processed': tracker.processed_requests,
                'completed_at': datetime.now().isoformat(),
                'logs': tracker.logs
            }

            if job_id in fuzzer_instances:
                del fuzzer_instances[job_id]
            if job_id in running_jobs:
                del running_jobs[job_id]

async def wait_for_resume(job_id: str, fuzzer: FuzzerManager):
    """
    Wait for job status to change from paused to something else
    """
    while job_id in running_jobs and running_jobs[job_id].get('status') == 'paused':
        await asyncio.sleep(0.5)

    # Stop it if it's stopped during puase
    if job_id in running_jobs and running_jobs[job_id].get('status') == 'stopped':
        fuzzer.stop()
        raise asyncio.CancelledError('Job stopped while paused.')
    
    fuzzer.resume()
    
def get_job_status_message(job_id: str):
    """
    Generate a status message for a job based on its current state.
    """
    if job_id in running_jobs:
        job = running_jobs[job_id]
        return {
            'type': 'status',
            'job_id': job_id,
            'data': {
                'status': job.get('status', 'unkown'),
                'progress': job.get('progress', 0),
                'urls_processed': job.get('urls_processed', 0),
                'total_urls': job.get('total_urls', 0),
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
                'progress': 100,
                'urls_processed': job.get('urls_processed', 0),
                'total_urls': job.get('total_urls', job.get('urls_processed', 0)),
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
    
def get_job_logs(job_id: str):
    """
    Retrieve logs for a specific job
    """
    if job_id in running_jobs and 'logs' in running_jobs[job_id]:
        return running_jobs[job_id]['logs']
    elif job_id in job_results and 'logs' in job_results[job_id]:
        return job_results[job_id]['logs']
    return []