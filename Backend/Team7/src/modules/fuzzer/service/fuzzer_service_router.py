from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
import logging
import json
import uuid
from datetime import datetime
import os
import asyncio

# Import the service modules
from Team7.src.modules.fuzzer.service.fuzzer_service import (
    FuzzerConfig,
    FuzzerJobResponse,
    FuzzerResults,
    running_jobs,
    fuzzer_instances,
    job_results,
    active_connections,
    run_fuzzer_task,
    get_job_status_message,
    get_job_logs
)

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fuzzer_router = APIRouter(prefix='/api/fuzzer', tags=['fuzzer'])

# Log Helper Functions
def add_log_entry(job_id: str, message: str):
    """
    Add a log entry to the job's log, mirroring crawler's approach.
    """
    timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    log_entry = f'[{timestamp}] {message}'

    # If the job is running
    if job_id in running_jobs:
        if 'logs' not in running_jobs[job_id]:
            running_jobs[job_id]['logs'] = []
        running_jobs[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to running job {job_id}: {message}')

    # If the job is already completed
    elif job_id in job_results:
        if 'logs' not in job_results[job_id]:
            job_results[job_id]['logs'] = []
        job_results[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to completed job {job_id}: {message}')

    else:
        logger.warning(f'Cannot add log for job {job_id}, job not found: {message}')

# Websocket handler
async def handle_fuzzer_websocket(websocket: WebSocket, job_id: str):
    logger.info(f'[Backend] Websocket connection opened for fuzzer job: {job_id}')
    await websocket.accept()

    logger.info('Active fuzzer jobs after accept: %s', list(running_jobs.keys()))

    # Register connection
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        # Send initial status
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

        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                if data.get('type') == 'command':
                    command = data.get('command')
                    if command == 'get_logs':
                        logs = get_job_logs(job_id)
                        logger.info(f"Sending {len(logs)} log entries via websocket for job {job_id}")
                        await websocket.send_json({
                            'type': 'logs',
                            'job_id': job_id,
                            'data': {'logs': logs}
                        })
            except json.JSONDecodeError:
                logger.error(f'Received invalid JSON from client: {message}')

    except WebSocketDisconnect:
        # Remove the websocket from active connections
        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]
        logger.info(f'Websocket disconnect for fuzzer job: {job_id}')

    except Exception as e:
        logger.error(f'Error in Websocket connection for fuzzer job {job_id}: {str(e)}')
        if job_id in active_connections and websocket in active_connections[job_id]:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]

@fuzzer_router.post('', response_model=FuzzerJobResponse)
async def start_fuzzer(config: FuzzerConfig, background_tasks: BackgroundTasks):
    logger.info(f'Received Fuzzer configuration: {config}')

    job_id = str(uuid.uuid4())
    running_jobs[job_id] = {
        'status': 'initializing',
        'created_at': datetime.now().isoformat(),
        'progress': 0,
        'urls_processed': 0,
        'total_urls': len(config.parameters) * (len(config.payloads or []) + (1 if config.payload_file else 0)),
        'logs': []
    }

    # Add initial log entry
    add_log_entry(job_id, f'Job created with configuration: {config.model_dump()}')

    await asyncio.sleep(1)
    background_tasks.add_task(run_fuzzer_task, job_id, config)

    return FuzzerJobResponse(
        job_id=job_id,
        message='Fuzzer started successfully!',
        status='initializing',
        progress=0,
        urls_processed=0,
        total_urls=running_jobs[job_id]['total_urls']
    )

@fuzzer_router.get('/{job_id}', response_model=FuzzerJobResponse)
async def get_fuzzer_status(job_id: str):
    logger.info(f'Getting status for fuzzer job: {job_id}')

    if job_id in running_jobs:
        job = running_jobs[job_id]
        logger.info(f'Job {job_id} is running with status: {job["status"]}')
        return FuzzerJobResponse(
            job_id=job_id,
            message=f'Fuzzer job is {job["status"]}',
            status=job['status'],
            progress=job.get('progress', 0),
            urls_processed=job.get('urls_processed', 0),
            total_urls=job.get('total_urls', 0)
        )

    if job_id in job_results:
        job = job_results[job_id]
        logger.info(f'Job {job_id} is completed with status: {job.get("status", "completed")}')
        return FuzzerJobResponse(
            job_id=job_id,
            message='Fuzzer job completed',
            status=job.get('status', 'completed'),
            progress=100 if job.get('status') == 'completed' else 0,
            urls_processed=job.get('urls_processed', 0),
            total_urls=job.get('total_urls', job.get('urls_processed', 0))
        )

    logger.warning(f'Fuzzer job {job_id} not found')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@fuzzer_router.get('/{job_id}/results', response_model=FuzzerResults)
async def get_fuzzer_results(job_id: str):
    logger.info(f"Getting results for job: {job_id}")
    add_log_entry(job_id, f"Results requested via API")

    if job_id in job_results:
        results_file = job_results[job_id].get('results_file')

        if results_file and os.path.exists(results_file):
            logger.info(f"Result file path: {results_file}")
            try:
                logger.info(f"Reading results from file: {results_file}")
                with open(results_file, 'r') as file:
                    data = json.load(file)
                    logger.info(f"Successfully loaded {len(data)} records from file")
                    add_log_entry(job_id, f"Results retrieved: {len(data)} records")
                    return FuzzerResults(results=data)
            except Exception as e:
                logger.error(f'Error reading fuzzer results: {e}')
                add_log_entry(job_id, f"Error reading results: {str(e)}")
                raise HTTPException(status_code=500, detail='Error reading fuzzer results')
        else:
            logger.warning(f"No result file found at path: {results_file}. Returning empty results.")
            add_log_entry(job_id, f"Result file not found at path: {results_file}")
            return FuzzerResults(results=[])

    if job_id in running_jobs:
        logger.info(f"Job {job_id} is still running, no results available yet.")
        add_log_entry(job_id, "Results requested but job is still running")
        raise HTTPException(status_code=202, detail='Job is still running, no results available yet.')

    logger.warning(f"Results for job {job_id} not found.")
    raise HTTPException(status_code=404, detail=f'Results for job {job_id} not found.')

@fuzzer_router.get('/{job_id}/logs')
async def get_fuzzer_logs(job_id: str):
    logger.info(f"Getting logs for job: {job_id}")

    if job_id not in running_jobs and job_id not in job_results:
        logger.warning(f"Fuzzer job {job_id} not found when requesting logs")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    logs = get_job_logs(job_id)
    logger.info(f"Returning {len(logs)} log entries for job {job_id}")
    add_log_entry(job_id, f"Logs requested via API, returning {len(logs)} entries")

    updated_logs = get_job_logs(job_id)
    return {'logs': updated_logs}

@fuzzer_router.post('/{job_id}/stop')
async def stop_fuzzer_job(job_id: str):
    logger.info(f"Request to stop fuzzer job: {job_id}")

    if job_id in running_jobs:
        add_log_entry(job_id, "Stop requested by user")

        running_jobs[job_id]['status'] = 'stopped'
        if job_id in fuzzer_instances:
            try:
                fuzzer_instances[job_id].stop()
                logger.info(f'Successfully called stop() on fuzzer for job {job_id}')
            except Exception as e:
                logger.error(f'Error stopping fuzzer for job {job_id}: {str(e)}')
                add_log_entry(job_id, f"Error during stop: {str(e)}")

        job_results[job_id] = {
            'status': 'stopped',
            'urls_processed': running_jobs[job_id].get('urls_processed', 0),
            'completed_at': datetime.now().isoformat(),
            'stopped_by_user': True,
        }

        if 'logs' in running_jobs[job_id]:
            job_results[job_id]['logs'] = running_jobs[job_id]['logs']
            logger.info(f"Transferred {len(running_jobs[job_id]['logs'])} log entries to job_results")

        # Broadcast stop message
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
        add_log_entry(job_id, "Job stopped successfully")
        return {'success': True, 'message': 'Job stopped successfully'}

    if job_id in job_results:
        add_log_entry(job_id, "Stop requested but job was already completed")
        return {'success': True, 'message': 'Job was already completed.'}

    logger.warning(f"Fuzzer job {job_id} not found when attempting to stop")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found.')

@fuzzer_router.post('/{job_id}/pause')
async def pause_fuzzer_job(job_id: str):
    logger.info(f"Request to pause fuzzer job: {job_id}")

    if job_id in running_jobs:
        running_jobs[job_id]['status'] = 'paused'
        add_log_entry(job_id, "Pause requested by user")

        if job_id in fuzzer_instances:
            fuzzer_instances[job_id].pause()
            logger.info(f'Successfully paused fuzzer for job {job_id}')

        # Broadcast the pause
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

    logger.warning(f"Fuzzer job {job_id} not found when attempting to pause")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found.')

@fuzzer_router.post('/{job_id}/resume')
async def resume_fuzzer_job(job_id: str):
    logger.info(f"Request to resume fuzzer job: {job_id}")

    if job_id in running_jobs:
        running_jobs[job_id]['status'] = 'running'
        add_log_entry(job_id, "Resume requested by user")

        if job_id in fuzzer_instances:
            fuzzer_instances[job_id].resume()
            logger.info(f'Successfully resumed fuzzer for job {job_id}')

        # Broadcast resume message
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

    logger.warning(f"Fuzzer job {job_id} not found when attempting to resume")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found.')

def get_service_routers():
    return [fuzzer_router]

def get_websocket_handlers():
    return {
        'fuzzer': handle_fuzzer_websocket
    }
