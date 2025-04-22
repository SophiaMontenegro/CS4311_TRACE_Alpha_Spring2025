# Team1/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from Team1.intrudertool.intruder_tool import IntruderTool
from typing import List, Dict

router = APIRouter()
tool = None
class URLRequest(BaseModel):
    url: str

@router.post("/parse_forms")
async def parse_forms(request: URLRequest):
    global tool
    try:
        tool = IntruderTool(request.url)
        status = tool.fetch_target()

        if status != 200:
            raise HTTPException(status_code=status, detail="Failed to fetch target URL")

        forms = tool.parse_forms()
        return {"forms": forms}

    except Exception as e:
        return {"error": str(e)}

class IndexRequest(BaseModel):
    index: int

@router.post("/select_form")
def select_form(request: IndexRequest):
    global tool
    if not tool or not tool.forms:
        raise HTTPException(status_code=400, detail="No forms parsed yet.")

    try:
        tool.select_form(request.index)
        return {"status": "form selected", "index": request.index}
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid form index")
