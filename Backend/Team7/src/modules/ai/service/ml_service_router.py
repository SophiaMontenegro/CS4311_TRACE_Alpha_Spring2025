from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
import logging
import uuid
import os
import json
from datetime import datetime
import asyncio

# Import service module
from Team7.src.modules.ai.service.ml_service import (
    MLConfig,
    MLJobResponse,
    CredentialResults,
    running_jobs,
    job_results,
    active_connections,
    run_ml_task,
    get_job_status_message,
    get_job_logs
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for ML service
ml_router = APIRouter(prefix="/api/ml", tags=["ml"])

# Log Helper Functions
def add_log_entry(job_id: str, message: str):
    """
    Add a log entry to the job's logs, whether it's running or completed.
    This ensures logs are stored in the correct place.
    """
    timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    log_entry = f'[{timestamp}] {message}'
    
    # Add to running_jobs if the job is running
    if job_id in running_jobs:
        if 'logs' not in running_jobs[job_id]:
            running_jobs[job_id]['logs'] = []
        running_jobs[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to running ML job {job_id}: {message}')
    
    # Add to job_results if the job is completed
    elif job_id in job_results:
        if 'logs' not in job_results[job_id]:
            job_results[job_id]['logs'] = []
        job_results[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to completed ML job {job_id}: {message}')
    
    # If job doesn't exist, just log it
    else:
        logger.warning(f'Cannot add log for ML job {job_id}, job not found: {message}')

# WebSocket handler for ML service
async def handle_ml_websocket(websocket: WebSocket, job_id: str):
    logger.info(f'[Backend] WebSocket connection opened for ML job: {job_id}') 

    await websocket.accept()

    logger.info('Active ML jobs after accept: %s', list(running_jobs.keys()))

    # Register the connection
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        # Send an initial status message
        initial_status = get_job_status_message(job_id)
        await websocket.send_json(initial_status)

        # Send progress immediately after status
        if job_id in running_jobs:
            await websocket.send_json({
                'type': 'progress',
                'job_id': job_id,
                'data': {
                    'progress': running_jobs[job_id].get('progress', 0),
                    'processed_requests': running_jobs[job_id].get('urls_processed', 0),
                    'total_requests': running_jobs[job_id].get('total_urls', 0),
                    'current_payload': running_jobs[job_id].get('last_row', {}).get('payload')
                }
            })

            # Send last row for immediate table preview
            if 'last_row' in running_jobs[job_id]:
                await websocket.send_json({
                    'type': 'new_row',
                    'job_id': job_id,
                    'data': {
                        'row': running_jobs[job_id]['last_row']
                    }
                })


        # Listen for client responses
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)

                # Handle client commands
                if data.get('type') == 'command':
                    command = data.get('command')

                    if command == 'get_logs':
                        # Send all logs
                        logs = get_job_logs(job_id)
                        logger.info(f"Sending {len(logs)} log entries via websocket for ML job {job_id}")
                        await websocket.send_json({
                            'type': 'logs',
                            'job_id': job_id,
                            'data': {'logs': logs}
                        })

            except json.JSONDecodeError:
                logger.error(f'Received invalid JSON from client: {message}')

    except WebSocketDisconnect:
        # Remove the connection from the list
        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]
        logger.info(f'WebSocket disconnected for ML job: {job_id}')

    except Exception as e:
        logger.error(f'Error in WebSocket connection for ML job {job_id}: {str(e)}')
        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]

# ML API endpoints
@ml_router.post("", response_model=MLJobResponse)
async def start_ml_job(config: MLConfig, background_tasks: BackgroundTasks):
    logger.info(f"Received ML configuration: {config}")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Register job
    running_jobs[job_id] = {
        'status': 'initializing',
        'created_at': datetime.now().isoformat(),
        'config': config.model_dump(),
        'progress': 0,
        'step': 'initializing',
        'logs': []
    }
    
    # Add initial log entry
    add_log_entry(job_id, f'ML job created with configuration: {config.model_dump()}')
    
    # Start ML job in background
    await asyncio.sleep(1)
    background_tasks.add_task(run_ml_task, job_id, config)
    
    return MLJobResponse(
        job_id=job_id,
        message='ML job started successfully!',
        status='initializing',
        progress=0,
        step='initializing',
        total_steps=3
    )

@ml_router.get("/{job_id}", response_model=MLJobResponse)
async def get_ml_job_status(job_id: str):
    logger.info(f'Getting status for ML job: {job_id}')
    
    # Check if job is running
    if job_id in running_jobs:
        job = running_jobs[job_id]
        logger.info(f'ML job {job_id} is running with status: {job["status"]}')
        return MLJobResponse(
            job_id=job_id,
            message=f"ML job is {job['status']}",
            status=job['status'],
            progress=job.get('progress', 0),
            step=job.get('step', 'initializing'),
            total_steps=3
        )
    
    # Check if job is completed
    if job_id in job_results:
        job = job_results[job_id]
        logger.info(f'ML job {job_id} is completed with status: {job.get("status", "completed")}')
        return MLJobResponse(
            job_id=job_id,
            message='ML job completed',
            status=job.get('status', 'completed'),
            progress=100 if job.get('status') == 'completed' else 0,
            step='completed' if job.get('status') == 'completed' else 'error',
            total_steps=3
        )
    
    # Job not found
    logger.warning(f'ML job {job_id} not found')
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

@ml_router.get("/{job_id}/results", response_model=CredentialResults)
async def get_ml_results(job_id: str):
    logger.info(f"Getting results for ML job: {job_id}")
    
    # Add a log entry for this request
    add_log_entry(job_id, f"Results requested via API")
    
    # Check if job is completed
    if job_id in job_results:
        logger.info(f"ML job {job_id} found in job_results with status: {job_results[job_id].get('status')}")
        
        results_file = job_results[job_id].get('results_file')
        logger.info(f"Result file path: {results_file}")

        if results_file and os.path.exists(results_file):
            try:
                logger.info(f"Reading ML results from file: {results_file}")
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded {len(data)} credential records from file")
                    add_log_entry(job_id, f"Results retrieved: {len(data)} credential records")
                    return CredentialResults(results=data)
            except Exception as e:
                logger.error(f'Error reading ML results: {e}')
                add_log_entry(job_id, f"Error reading ML results: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error reading ML results: {str(e)}")
        else:
            # Return empty results if file doesn't exist
            logger.warning(f"Result file not found at path: {results_file}")
            add_log_entry(job_id, f"Result file not found at path: {results_file}")
            return CredentialResults(results=[])
    
    # If job is still running, return current results
    if job_id in running_jobs:
        logger.info(f"ML job {job_id} is still running with status: {running_jobs[job_id].get('status')}")
        add_log_entry(job_id, "Results requested but job is still running")
        raise HTTPException(status_code=202, detail="Job is still running, no results available yet")
    
    # Job not found or no results
    logger.warning(f"ML job {job_id} not found in either running_jobs or job_results")
    raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")

@ml_router.get("/{job_id}/logs")
async def get_ml_logs(job_id: str):
    logger.info(f"Getting logs for ML job: {job_id}")
    
    # Check if job exists
    if job_id not in running_jobs and job_id not in job_results:
        logger.warning(f"ML job {job_id} not found when requesting logs")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get logs using the helper function
    logs = get_job_logs(job_id)
    
    # Log the number of logs being returned
    logger.info(f"Returning {len(logs)} log entries for ML job {job_id}")
    
    # Add a self-referential log entry
    add_log_entry(job_id, f"Logs requested via API, returning {len(logs)} entries")
    
    # Get updated logs (including the one we just added)
    updated_logs = get_job_logs(job_id)
    
    # Return the logs
    return {'logs': updated_logs}

@ml_router.post('/{job_id}/stop')
async def stop_ml_job(job_id: str):
    logger.info(f"Request to stop ML job: {job_id}")
    
    if job_id in running_jobs:
        # Add log entry
        add_log_entry(job_id, "Stop requested by user")
        
        # Update the status to stop the loop
        running_jobs[job_id]['status'] = 'stopped'

        # Move the job from running to results with an updated state
        job_results[job_id] = {
            'status': 'stopped',
            'completed_at': datetime.now().isoformat(),
            'stopped_by_user': True
        }

        # Copy the logs over
        if 'logs' in running_jobs[job_id]:
            job_results[job_id]['logs'] = running_jobs[job_id]['logs'].copy()  # Create a copy to prevent reference issues
            logger.info(f"Transferred {len(running_jobs[job_id]['logs'])} log entries to job_results")

        # Broadcast the stop message to the connected clients
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

        # Remove from the running jobs list
        del running_jobs[job_id]
        
        # Final log entry
        add_log_entry(job_id, "ML job stopped successfully")

        return {'success': True, 'message': 'Job stopped successfully'}
    
    # if the job isn't in the running_jobs but is already finished.
    if job_id in job_results:
        add_log_entry(job_id, "Stop requested but ML job was already completed")
        return {'success': True, 'message': 'Job was already completed.'}
    
    # If no job was found in either
    logger.warning(f"ML job {job_id} not found when attempting to stop")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

# Function to get ML router for main.py
def get_service_routers():
    return [ml_router]

# Function to register websocket handlers
def get_websocket_handlers():
    return {
        "ml": handle_ml_websocket
    }