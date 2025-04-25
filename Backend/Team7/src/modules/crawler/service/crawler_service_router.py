from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
import logging
import json
import uuid
from datetime import datetime
import os
import asyncio

# Import the service modules
from Team7.src.modules.crawler.service.crawler_service import (
    CrawlerConfig,
    CrawlerJobResponse,
    CrawlerResults,
    running_jobs,
    crawler_instances,
    job_results,
    active_connections,
    run_crawler_task,
    get_job_status_message,
    get_job_logs
)

# Set up log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the routes for the different services
crawler_router = APIRouter(prefix='/api/crawler', tags=['crawler'])

# Websocket handler for the crawler service
async def handle_crawler_websocket(websocket: WebSocket, job_id: str):
    logger.info(f'[Backend] Websocket connection opened for job: {job_id}')

    await websocket.accept()

    logger.info('Active jobs after accept: %s', list(running_jobs.keys()))

    # Register the connection
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        #Send a status message
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

            # Ssend last row for immediate table preview
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
        # If disconnected remove the connection from list
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
        logger.info(f'Added log to running job {job_id}: {message}')
    
    # Add to job_results if the job is completed
    elif job_id in job_results:
        if 'logs' not in job_results[job_id]:
            job_results[job_id]['logs'] = []
        job_results[job_id]['logs'].append(log_entry)
        logger.info(f'Added log to completed job {job_id}: {message}')
    
    # If job doesn't exist, just log it
    else:
        logger.warning(f'Cannot add log for job {job_id}, job not found: {message}')

# Crawler API endpoints
@crawler_router.post('', response_model=CrawlerJobResponse)
async def start_crawler(config: CrawlerConfig, background_tasks: BackgroundTasks):
    logger.info(f'Received crawler configuration: {config}')

    # Generate a uniques job ID
    job_id = str(uuid.uuid4())

    # Register the job
    running_jobs[job_id] = {
        'status': 'initializing',
        'created_at': datetime.now().isoformat(),
        'progress': 0,
        'urls_processed': 0,
        'total_urls': config.limit or 0,
        'logs': []  # Initialize empty logs list
    }
    
    # Add initial log entry
    add_log_entry(job_id, f'Job created with configuration: {config.model_dump()}')

    # Start crawler in background
    await asyncio.sleep(1)
    background_tasks.add_task(run_crawler_task, job_id, config)

    return CrawlerJobResponse(
        job_id=job_id,
        message='Crawler started successfully!',
        status='initializing',
        progress=0,
        urls_processed=0,
        total_urls=config.limit or 0
    )

@crawler_router.get('/{job_id}', response_model=CrawlerJobResponse)
async def get_crawler_status(job_id: str):
    logger.info(f'Getting status for job: {job_id}')
    
    # Check if the job is running
    if job_id in running_jobs:
        job = running_jobs[job_id]
        logger.info(f'Job {job_id} is running with status: {job["status"]}')
        return CrawlerJobResponse(
            job_id=job_id,
            message=f"Crawler job is {job['status']}",
            status=job['status'],
            progress=job.get('progress', 0),
            urls_processed=job.get('urls_processed', 0),
            total_urls=job.get('total_urls', 0),
        )
    
    # Check if the job is completed
    if job_id in job_results:
        job = job_results[job_id]
        logger.info(f'Job {job_id} is completed with status: {job.get("status", "completed")}')
        return CrawlerJobResponse(
            job_id=job_id,
            message='Crawler job completed',
            status=job.get('status', 'completed'),
            progress=100 if job.get('status') == 'completed' else 0,
            urls_processed=job.get('urls_processed', 0),
            total_urls=job.get('total_urls', job.get('urls_processed', 0))
        )
    
    # Job isn't found
    logger.warning(f'Job {job_id} not found')
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@crawler_router.get('/{job_id}/results', response_model=CrawlerResults)
async def get_crawler_results(job_id: str):
    logger.info(f"Getting results for job: {job_id}")
    
    # Add a log entry for this request
    add_log_entry(job_id, f"Results requested via API")
    
    # Check if job is completed
    if job_id in job_results:
        logger.info(f"Job {job_id} found in job_results with status: {job_results[job_id].get('status')}")
        
        result_file = job_results[job_id].get('result_file')
        logger.info(f"Result file path: {result_file}")

        if result_file and os.path.exists(result_file):
            try:
                logger.info(f"Reading results from file: {result_file}")
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded {len(data)} records from file")
                    add_log_entry(job_id, f"Results retrieved: {len(data)} records")
                    return CrawlerResults(results=data)
            except Exception as e:
                logger.error(f'Error reading crawler results: {e}')
                add_log_entry(job_id, f"Error reading results: {str(e)}")
                raise HTTPException(status_code=500, detail=f'Error reading crawler results: {str(e)}')
        else:
            # If the file doesn't exist, try to check if there are results in memory
            logger.warning(f"Result file not found at path: {result_file}")
            add_log_entry(job_id, f"Result file not found at path: {result_file}")
            
            # Try to load from crawler_table_data.json as fallback
            try:
                if os.path.exists("Team7/src/database/crawler/crawler_table_data.json"):
                    logger.info("Attempting to read from crawler_table_data.json as fallback")
                    with open("Team7/src/database/crawler/crawler_table_data.json", 'r') as f:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data)} records from fallback file")
                        add_log_entry(job_id, f"Results retrieved from fallback: {len(data)} records")
                        return CrawlerResults(results=data)
            except Exception as e:
                logger.error(f'Error reading fallback crawler results: {e}')
                add_log_entry(job_id, f"Error reading fallback results: {str(e)}")
            
            # Return empty results if no data is available
            logger.info("No results file found, returning empty results")
            add_log_entry(job_id, "No results file found, returning empty results")
            return CrawlerResults(results=[])
                
    # If job is still running, return current results
    if job_id in running_jobs:
        logger.info(f"Job {job_id} is still running with status: {running_jobs[job_id].get('status')}")
        add_log_entry(job_id, "Results requested but job is still running")
        raise HTTPException(status_code=202, detail="Job is still running, no results available yet.")
    
    # Job not found or no results
    logger.warning(f"Job {job_id} not found in either running_jobs or job_results")
    raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found.")

@crawler_router.get('/{job_id}/logs')
async def get_crawler_logs(job_id: str):
    logger.info(f"Getting logs for job: {job_id}")
    
    # Check if job exists
    if job_id not in running_jobs and job_id not in job_results:
        logger.warning(f"Job {job_id} not found when requesting logs")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get logs using the helper function
    logs = get_job_logs(job_id)
    
    # Log the number of logs being returned
    logger.info(f"Returning {len(logs)} log entries for job {job_id}")
    
    # Add a self-referential log entry
    add_log_entry(job_id, f"Logs requested via API, returning {len(logs)} entries")
    
    # Get updated logs (including the one we just added)
    updated_logs = get_job_logs(job_id)
    
    # Return the logs
    return {'logs': updated_logs}

@crawler_router.post('/{job_id}/stop')
async def stop_crawler_job(job_id: str):
    logger.info(f"Request to stop job: {job_id}")
    
    if job_id in running_jobs:
        # Add log entry
        add_log_entry(job_id, "Stop requested by user")
        
        # Update the status to stop the loop
        running_jobs[job_id]['status'] = 'stopped'

        # Stop the crawler or task instance
        if job_id in crawler_instances:
            try:
                crawler_instances[job_id].stop()
                logger.info(f"Successfully called stop() on crawler for job {job_id}")
            except Exception as e:
                logger.error(f"Error stopping crawler for job {job_id}: {str(e)}")
                add_log_entry(job_id, f"Error during stop: {str(e)}")

        # Move the job from running to results with an updated state
        job_results[job_id] = {
            'status': 'stopped',
            'urls_processed': running_jobs[job_id].get('urls_processed', 0),
            'completed_at': datetime.now().isoformat(),
            'stopped_by_user': True
        }

        # Copy the logs over
        if 'logs' in running_jobs[job_id]:
            job_results[job_id]['logs'] = running_jobs[job_id]['logs']
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
        add_log_entry(job_id, "Job stopped successfully")

        return {'success': True, 'message': 'Job stopped successfully'}
    
    # if the job isn't in the running_jobs but is already finished.
    if job_id in job_results:
        add_log_entry(job_id, "Stop requested but job was already completed")
        return {'success': True, 'message': 'Job was already completed.'}
    
    # If no job was found in either
    logger.warning(f"Job {job_id} not found when attempting to stop")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@crawler_router.post('/{job_id}/pause')
async def pause_crawler_job(job_id: str):
    logger.info(f"Request to pause job: {job_id}")
    
    if job_id in running_jobs:
        running_jobs[job_id]['status'] = 'paused'
        
        # Add log entry
        add_log_entry(job_id, "Pause requested by user")

        # Pause the crawler
        if job_id in crawler_instances:
            crawler_instances[job_id].pause()
            logger.info(f"Successfully paused crawler for job {job_id}")

        # Broadcast that the job has been paused
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

    logger.warning(f"Job {job_id} not found when attempting to pause")
    raise HTTPException(status_code=404, detail=f'Job {job_id} not found')

@crawler_router.post("/{job_id}/resume")
async def resume_crawler_job(job_id: str):
    logger.info(f"Request to resume job: {job_id}")
    
    if job_id in running_jobs:
        running_jobs[job_id]["status"] = "running"
        
        # Add log entry
        add_log_entry(job_id, "Resume requested by user")

        # Resume the crawler
        if job_id in crawler_instances:
            crawler_instances[job_id].resume()
            logger.info(f"Successfully resumed crawler for job {job_id}")
            
        # Broadcast resume message to all connected clients
        if job_id in active_connections:
            resume_message = {
                "type": "status", 
                "job_id": job_id, 
                "data": {"status": "running"}
            }
            for websocket in active_connections[job_id]:
                try:
                    await websocket.send_json(resume_message)
                except Exception as e:
                    logger.error(f"Error sending resume message to WebSocket: {str(e)}")
                    
        return {"success": True, "message": "Job resumed successfully"}
    
    logger.warning(f"Job {job_id} not found when attempting to resume")
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

# Function to get all the routers for main.py
def get_service_routers():
    return [crawler_router]

# Function to register websocket handlers
def get_websocket_handlers():
    return {
        'crawler': handle_crawler_websocket
    }