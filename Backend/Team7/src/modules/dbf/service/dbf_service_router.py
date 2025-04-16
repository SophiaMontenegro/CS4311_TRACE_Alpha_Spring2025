from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
import logging
import json
import uuid
from datetime import datetime
import os

# Import the service module
from Team7.src.modules.dbf.service.dbf_service import (
    DBFConfig,
    DBFJobResponse,
    DBFResults,
    running_jobs,
    dbf_instances,
    job_results,
    active_connections,
    run_dbf_task,
    get_job_status_message,
    get_job_logs
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the routes for the different service
dbf_router = APIRouter(prefix='/api/dbf', tags=['dbf'])

# Websocket handler for the DBF service
async def handle_dbf_websocket(websocket: WebSocket, job_id: str):
    logger.info(f'[Backend] Websocket connection opened for job: {job_id}')

    await websocket.accept()

    logger.info(f'Active jobs after accept: {running_jobs.keys()}')

    # Register connections
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        # Send initial message
        initial_status = get_job_status_message(job_id)
        await websocket.send_json(initial_status)

        while True:
            message = await websocket.receive_text()
            try: 
                data = json.loads(message)

                if data.get('type') == 'command':
                    command = data.get('command')

                    if command == 'get_logs':
                        logs = get_job_logs(job_id)
                        logger.info(f'Sending {len(logs)} log entries via websocket for job {job_id}')
                        await websocket.send_json({
                            'type': 'logs',
                            'job_id': job_id,
                            'data': {'logs': logs}
                        })
            
            except json.JSONDecodeError:
                logger.error(f'Received invalid JSON from client: {message}')

    except WebSocketDisconnect:
        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]

        logger.info(f'Websocket disconnect for job: {job_id}, job stopped')

    except Exception as e:
        logger.error(f'Error in Websocket connection for job {job_id}: {str(e)}')

        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]

# Log Helper Function
def add_log_entry(job_id: str, message: str):
    """
    Add a log entry to the job's log
    """
    timestamp = datetime.now().isoformat()
    log_entry = f'[{timestamp}] {message}'

    # Add logs to running_jobs if running
    if job_id in running_jobs:
        if 'logs' not in running_jobs[job_id]:
            running_jobs[job_id] = []
        running_jobs[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to running jobs {job_id}: {message}')

    # Add to job_results if completed
    elif job_id in job_results:
        if 'logs' not in job_results[job_id]:
            job_results[job_id]['logs'] = []
        job_results[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to completed job {job_id}: {message}')

    else:
        logger.warning(f'Cannot add log for job {job_id}, job not found: {message}')

# DBF API endpoints
@dbf_router.post('', response_model=DBFJobResponse)
async def start_dbf(config: DBFConfig, background_tasks: BackgroundTasks):
    logger.info(f'Received DBF configuration: {config}')

    job_id = str(uuid.uuid4())

    # Register the job
    running_jobs[job_id] = {
        'status': 'initializing',
        'created_at': datetime.now().isoformat(),
        'progress': 0,
        'processed_requests': 0,
        'filtered_requests': 0,
        'requests_per_second': 0,
        'logs': []
    }

    # Add initial log entry
    add_log_entry(job_id, f'Job created with configuration: {config.model_dump()}')

    background_tasks.add_task(run_dbf_task, job_id, config)

    return DBFJobResponse(
        job_id=job_id,
        message='Directory Brute Roce scan started successfully',
        status='initializing',
        progress=0,
        processed_requests=0,
        filtered_requests=0,
        requests_per_second=0
    )

@dbf_router.get('/{job_id}', response_model=DBFJobResponse)
async def get_dbf_status(job_id: str):
    logger.info(f'Getting status for job: {job_id}')

    # Check if running
    if job_id in running_jobs:
        job = running_jobs[job_id]
        logger.info(f'Job {job_id} is running with status: {job['status']}')
        return DBFJobResponse(
            job_id=job_id,
            message=f'DBF job is {job['status']}',
            status=job['status'],
            progress=job.get('progress', 0),
            processed_requests=job.get('processed_requests', 0),
            filtered_requests=job.get('filtered_requests', 0),
            requests_per_second=job.get('requests_per_second', 0),
        )
    
    # Check if completed
    if job_id in job_results:
        job = job_results[job_id]
        logger.info(f'Job {job_id} is completed with status: {job.get('status', 'completed')}')
        return DBFJobResponse(
            job_id=job_id,
            message='DBF job completed',
            status=job.get('status', 'completed'),
            progress = 100 if job.get('status') == 'completed' else 0,
            processed_requests=job.get('processed_requests', 0),
            filtered_requests=job.get('filtered_requests', 0),
            requests_per_second=job.get('requests_per_second', 0),
        )
    
    # Job not found
    logger.warning(f'Job {job_id} not found')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@dbf_router.get('/{job_id}/results', response_model=DBFResults)
async def get_dbf_results(job_id: str):
    logger.info(f'Getting results for job: {job_id}')

    add_log_entry(job_id, f'Results requested via API')

    # Check if completed
    if job_id in job_results:
        logger.info(f'Job {job_id} found in job_results with status: {job_results[job_id].get('status')}')

        results_file = job_results[job_id].get('results_file')
        logger.info(f'Result file path: {results_file}')

        if results_file and os.path.exists(results_file):
            try:
                # TODO: Update the path to the database folder.
                logger.info(f'Reading results from file: {results_file}')
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f'Successfully loaded {len(data)} records from file')
                    add_log_entry(job_id, f'Results retrieved: {len(data)} records')
                return DBFResults(results=data)
            except Exception as e:
                logger.error(f'Error reading DBF results: {e}')
                add_log_entry(job_id, f'Error reading results: {str(e)}')
                raise HTTPException(status_code=500, detail=f'Error reading DBF results: {str(e)}')
            
        else:
            # If the file doesn't exist or the path
            logger.warning(f'Result file not found at path: {results_file}')
            add_log_entry(job_id, f'Result file not found at path: {results_file}')
            return DBFResults(results=[])
        
    # If the job is still running
    if job_id in running_jobs:
        logger.info(f'Job {job_id} is still running with status: {running_jobs[job_id].get('status')}')
        add_log_entry(job_id, 'Results requested but job is still running')
        raise HTTPException(status_code=202, detail='Job is still running, no results available yet.')
    
    # Job isn't found
    logger.warning(f'Job {job_id} not found in either running_jobs or job_results')
    raise HTTPException(status_code=404, detail=f'Results for job {job_id} not found.')

@dbf_router.get('/{job_id}/logs')
async def get_dbf_logs(job_id: str):
    logger.info(f'Getting logs for job: {job_id}')

    if job_id not in running_jobs and job_id not in job_results:
        logger.warning(f'Job {job_id} not found when requesting logs')
        raise HTTPException(status_code=404, detail=f'Job {job_id} not found')
    
    logs = get_job_logs(job_id)

    logger.info(f'Returning {len(logs)} log entries for job {job_id}')
    add_log_entry(job_id, f'Logs requested via API, returning {len(logs)} entries')

    updated_logs = get_job_logs(job_id)
    return {'logs': updated_logs}

@dbf_router.post('/{job_id}/stop')
async def stop_dbf_job(job_id: str):
    logger.info(f'Request to stop job: {job_id}')

    if job_id and running_jobs:
        add_log_entry(job_id, 'Stop requested by user')

        running_jobs[job_id]['status'] = 'stopped'

        if job_id in dbf_instances:
            try:
                dbf_instances[job_id].stop()
                logger.info(f'Successfully called stop() on DBF for job {job_id}')
            except Exception as e:
                logger.error(f'Error stopping DBF for job {job_id}: {str(e)}')
                add_log_entry(job_id, f'Error during stop: {str(e)}')

        job_results[job_id] = {
            'status': 'stopped',
            'urls_processed': running_jobs[job_id].get('urls_processed', 0),
            'completed_at': datetime.now().isoformat(),
            'stopped_by_user': True
        }

        if 'logs' in running_jobs[job_id]:
            job_results[job_id]['logs'] = running_jobs[job_id]['logs']
            logger.info(f'Transferred {len(running_jobs[job_id]['logs'])} log entries to job_results')

        if job_id in active_connections:
            stop_message = {
                'type': 'status',
                'job_id': job_id,
                'data': {'status': 'stopped'}
            }
            for websocket in active_connections[job_id]:
                try:
                    await websocket.send_json(stop_message)
                except Exception as e:
                    logger.error(f'Error sending stop message to WebSocket: {str(e)}')

        del running_jobs[job_id]
        add_log_entry(job_id, 'Job stopped successfully')

        return {'success': True, 'message': 'Job stopped successfully'}
    
    # If the job is already finished
    if job_id in job_results:
        add_log_entry(job_id, 'Stop requested but job was already completed')
        return {'success': True, 'message': 'Job was already completed.'}
    
    # If job not found
    logger.warning(f'Job {job_id} not found when attempting to stop')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@dbf_router.post('/{job_id}/pause')
async def pause_dbf_job(job_id: str):
    logger.info(f'Request to pause job: {job_id}')

    if job_id in running_jobs:
        running_jobs[job_id]['status'] = 'paused'

        add_log_entry(job_id, 'Pause requested by user')

        # Pause the instance
        if job_id in dbf_instances:
            dbf_instances[job_id].pause()
            logger.info(f'Successfully paused DBF for job {job_id}')

        if job_id in active_connections:
            pause_message = {
                'type': 'status',
                'job_id': job_id,
                'data': {'status': 'paused'}
            }
            for websocket in active_connections[job_id]:
                try:
                    await websocket.send_json(pause_message)
                except Exception as e:
                    logger.error(f'Error sending pause message to WebSocket: {str(e)}')

        return {'success': True, 'message': 'Job paused successfully'}
    
    logger.warning(f'Job {job_id} not found when attempting to pause')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@dbf_router.post('/{job_id}/resume')
async def resume_crawler_job(job_id: str):
    logger.info(f'Request to resume job: {job_id}')

    if job_id in running_jobs:
        running_jobs[job_id]['status'] = 'running'

        add_log_entry(job_id, 'Resume requested by user')

        if job_id in dbf_instances:
            dbf_instances[job_id].resume()
            logger.info(f'Successfully resumed DBF for job {job_id}')

        if job_id in active_connections:
            resume_message = {
                'type': 'status',
                'job_id': job_id,
                'data': {'status': 'running'}
            }
            for websocket in active_connections[job_id]:
                try: 
                    await websocket.send_json(resume_message)
                except Exception as e:
                    logger.error(f'Error sending resume message to WebSocket: {str(e)}')

        return {'success': True, 'message': 'Job resumed successfully'}
    
    logger.warning(f'Job {job_id} not found when attempting to resume')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

def get_service_routers():
    return [dbf_router]

def get_websocket_handlers():
    return {
        'dbf': handle_dbf_websocket
    }