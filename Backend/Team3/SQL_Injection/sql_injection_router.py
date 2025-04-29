import logging
import os
import shutil
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from .sql_runner.sqlmap_runner import handle_sqlmap_request

from Team3.Database.File_Manager import FileManager
from Team3.Database.Database_Manager import Database_Manager

logger = logging.getLogger(__name__)

router = APIRouter()

db_manager = Database_Manager()
file_manager = FileManager(db_manager)

RESULTS_DIR = "Team3/SQL_Injection/sqlmap_results"

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

@router.get("/sqlmap/results/{project_name}/{job_id}")
async def get_sqlmap_results(project_name: str, job_id: str):
    tool_name = "SQLInjection"
    """Returns information about a specific SQLMap job, including file paths"""
    logger.debug(f"Fetching results for SQL injection job: {job_id}")

    try:
        # Retrieving tool directory to save files
        tool_directory = file_manager.get_tool_directory(project_name, tool_name) # return the path for SQL
        if not tool_directory:
            raise HTTPException(status_code=404, detail=f"Tool directory not found for project '{project_name}' and tool '{tool_name}'")
        print("✅ Tool Directory:", tool_directory)
        # Move result_file and log_file to my tool_directory

        # Construct paths based on the job_id
        # results_dir = "sqlmap_results"
        source_result = f"Team3/SQL_Injection/sqlmap_results/sql_results_{job_id}.csv"
        source_log = f"Team3/SQL_Injection/sqlmap_results/sql_log_{job_id}.csv"
        result_filename = f"sql_results_{job_id}.csv"
        log_filename = f"sql_log_{job_id}.csv"

        
        result_path = os.path.join(tool_directory, result_filename) # adding the results
        log_path = os.path.join(tool_directory, log_filename) # adding the log

        shutil.move(source_result, result_path)
        shutil.move(source_log, log_path)

        # Update database with job_id
        append_success = file_manager.append_job_id_to_tool(project_name, tool_name, job_id)
        if not append_success:
            raise HTTPException(status_code=500, detail="Failed to append job_id to tool")

        """
        file_success = file_manager.append_job_id_to_tool(project_name, job_id, result_filename, tool_directory, islog)
        if not file_success:
            raise HTTPException(status_code=500, detail="Failed to append job_id to tool")
        """
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


    except Exception as e: # here
        logger.error(f"Error fetching SQL injection results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sqlmap/csv/{project_name}/{job_id}")
async def get_sqlmap_csv(project_name: str, job_id: str):
    """Returns the raw CSV content for a specific SQLMap job"""
    logger.debug(f"Fetching CSV for SQL injection job: {job_id}")
    tool_name = "SQLInjection"
    try:
        # Retrieving tool directory to save files
        results_dir = file_manager.get_tool_directory(project_name, tool_name)
        if not results_dir:
            raise HTTPException(status_code=404, detail=f"Tool directory not found for project '{project_name}' and tool '{tool_name}'")

        #results_dir = "sqlmap_results"
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
