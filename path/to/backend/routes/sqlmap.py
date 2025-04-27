from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from typing import Dict, Any

router = APIRouter(prefix="/sqlmap", tags=["sqlmap"])

# Assuming a base directory where all job results are stored
RESULTS_BASE_DIR = "path/to/sqlmap/results"

@router.get("/results/{job_id}")
async def get_sqlmap_results(job_id: str) -> Dict[str, Any]:
    """Returns information about a specific SQLMap job, including file paths"""
    job_dir = os.path.join(RESULTS_BASE_DIR, job_id)
    
    if not os.path.exists(job_dir):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get CSV file path
    csv_path = os.path.join(job_dir, f"{job_id}_results.csv")
    
    # Check if CSV file exists
    csv_exists = os.path.exists(csv_path)
    
    # Return job information
    return {
        "job_id": job_id,
        "status": "completed",  # You might want to retrieve this from a DB
        "csv_path": csv_path if csv_exists else None,
        "files": {
            "csv": csv_path if csv_exists else None,
            # Add other files if needed
        }
    }

@router.get("/csv/{job_id}")
async def get_sqlmap_csv(job_id: str):
    """Returns the raw CSV content for a specific SQLMap job"""
    job_dir = os.path.join(RESULTS_BASE_DIR, job_id)
    csv_path = os.path.join(job_dir, f"{job_id}_results.csv")
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail=f"CSV file for job {job_id} not found")
    
    # Return the file as a downloadable response
    return FileResponse(
        path=csv_path,
        filename=f"{job_id}_results.csv",
        media_type="text/csv"
    )