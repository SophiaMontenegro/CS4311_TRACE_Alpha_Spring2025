from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from Team1.httpclient.http_client_service import (
    send_http_request_service,
    get_http_job,
    get_http_job_logs
)

router = APIRouter()

@router.post("/send")
async def send_http_request(request: Request):
    """
    Endpoint to send an HTTP request to a specified target system.
    Creates a new job and immediately returns the HTTP response.
    """
    try:
        # Parse JSON payload
        data = await request.json()
        target_system = data.get("target")
        crafted_request = data.get("request")
        project_name = data.get("project") or "default_project"  # real project name support for future 

        # Validate required fields
        if not target_system or not crafted_request:
            raise HTTPException(status_code=400, detail="Target system and request must be provided.")

        # Create a new HTTP job
        result = send_http_request_service(target_system, crafted_request, project_name)

        # Retrieve the created job to fetch the full response
        job = get_http_job(result['job_id'])
        if not job:
            raise HTTPException(status_code=500, detail="Job creation failed.")

        # Return only the response part to the frontend
        return JSONResponse(content=job['response'])

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/{job_id}")
async def get_http_request_response(job_id: str):
    """
    Endpoint to retrieve the stored HTTP job by its ID.
    """
    job = get_http_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return job


@router.get("/{job_id}/logs")
async def get_http_request_logs(job_id: str):
    """
    Endpoint to retrieve logs associated with a specific HTTP job.
    """
    logs = get_http_job_logs(job_id)
    if not logs:
        raise HTTPException(status_code=404, detail=f"No logs found for job {job_id}.")
    return {"logs": logs}
