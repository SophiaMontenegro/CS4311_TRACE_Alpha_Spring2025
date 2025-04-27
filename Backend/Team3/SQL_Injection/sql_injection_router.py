import logging
import os
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from .sql_runner.sqlmap_runner import handle_sqlmap_request

logger = logging.getLogger(__name__)

router = APIRouter()

class SQLInjectionRequest(BaseModel):
    target_url: str
    port: str
    injectable_params: str = None
    custom_flags: str = None

@router.post("/sqlmap/scan")
async def start_sql_injection_scan(request: SQLInjectionRequest):
    logger.debug(f"Received SQL injection scan request: {request.dict()}")
    try:
        result = handle_sqlmap_request(request.dict())
        logger.debug(f"SQL injection scan result: {result}")
        return {"job_id": result["job_id"], "message": "SQL Injection scan started"}
    except Exception as e:
        logger.error(f"Error starting SQL injection scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sqlmap/history")
async def get_sql_injection_history():
    logger.debug("Fetching SQL injection scan history")
    try:
        # Implement the logic to fetch history from your storage (e.g., database or file)
        # For now, we'll return an empty list
        return {"history": []}
    except Exception as e:
        logger.error(f"Error fetching SQL injection history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching scan history")

@router.get("/sqlmap/results/{job_id}")
async def get_sqlmap_results(job_id: str):
    """Returns information about a specific SQLMap job, including file paths"""
    logger.debug(f"Fetching results for SQL injection job: {job_id}")
    try:
        # Construct paths based on the job_id
        results_dir = "sqlmap_results"
        result_filename = f"sql_results_{job_id}.csv"
        log_filename = f"sql_log_{job_id}.csv"
        
        result_path = os.path.join(results_dir, result_filename)
        log_path = os.path.join(results_dir, log_filename)
        
        # Check if results file exists
        if not os.path.exists(result_path):
            logger.warning(f"Results file not found for job {job_id}")
            return {"job_id": job_id, "status": "running", "result_file": None}
        
        # Return job information
        return {
            "job_id": job_id,
            "status": "completed",
            "result_file": result_path,
            "log_file": log_path
        }
    except Exception as e:
        logger.error(f"Error fetching SQL injection results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sqlmap/csv/{job_id}")
async def get_sqlmap_csv(job_id: str):
    """Returns the raw CSV content for a specific SQLMap job"""
    logger.debug(f"Fetching CSV for SQL injection job: {job_id}")
    try:
        results_dir = "sqlmap_results"
        result_filename = f"sql_results_{job_id}.csv"
        csv_path = os.path.join(results_dir, result_filename)
        
        if not os.path.exists(csv_path):
            logger.warning(f"CSV file not found for job {job_id}")
            raise HTTPException(status_code=404, detail=f"CSV file for job {job_id} not found")
        
        # Read the CSV file
        with open(csv_path, "r", encoding="utf-8") as csv_file:
            csv_content = csv_file.read()
        
        # Return CSV content with appropriate headers
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sql_results_{job_id}.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SQL injection CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_service_routers():
    logger.debug("Getting SQL injection service routers")
    return [router]

def get_websocket_handlers():
    # Implement WebSocket handlers if needed
    return {}