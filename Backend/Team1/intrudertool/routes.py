# Team1/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from Team1.intrudertool.intruder_tool import IntruderTool


router = APIRouter()

class URLRequest(BaseModel):
    url: str

@router.post("/parse_forms")
async def parse_forms(request: URLRequest):
    try:
        tool = IntruderTool(request.url)
        status = tool.fetch_target()

        if status != 200:
            raise HTTPException(status_code=status, detail="Failed to fetch target URL")

        forms = tool.parse_forms()
        return {"forms": forms}

    except Exception as e:
        return {"error": str(e)}