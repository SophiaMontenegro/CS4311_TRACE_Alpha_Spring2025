# Team1/routes.py (updated with /reconnaissance)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Team1.intrudertool.intruder_tool import IntruderTool
from typing import List, Dict, Optional

router = APIRouter()
tool = None

class URLRequest(BaseModel):
    url: str

@router.post("/reconnaissance")
def reconnaissance(request: URLRequest):
    global tool
    tool = IntruderTool(request.url)

    if not tool.is_valid_url():
        raise HTTPException(status_code=400, detail="Invalid URL.")

    mode = tool.detect_mode()
    print(f"\nDetected mode: {mode}")
    if mode == "html":
        status = tool.fetch_target()
        if status != 200:
            raise HTTPException(status_code=400, detail=f"Failed to fetch HTML content (Status {status})")
        
        forms = tool.parse_forms()

        if not forms:
            # If no forms found even though HTML, fallback to URL attack
            return {"mode": "url", "forms": [], "message": "No forms found, switching to URL attack."}

        return {"mode": "html", "forms": forms}

    elif mode == "json":
        # No need to fetch forms here
        return {"mode": "json", "forms": []}

    elif mode == "url":
        # No forms for URL attacks
        return {"mode": "url", "forms": []}

    else:
        raise HTTPException(status_code=400, detail="Unknown or unsupported mode.")


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

@router.get("/preview_request")
def preview_request():
    global tool
    if not tool:
        raise HTTPException(status_code=400, detail="Tool not initialized.")

    if tool.selected_form_index is None:
        return {"error": "No form selected, cannot preview."}

    preview = tool.get_http_request_preview()
    return preview


class AttackRequest(BaseModel):
    intrusion_field: str
    payloads: List[str]
    attack_type: str  # 'html_form', 'api', or 'urlencoded'
    api_endpoint: Optional[str] = None
    base_body: Optional[Dict] = None
    headers: Optional[Dict] = None
    param_name: Optional[str] = None

@router.post("/run_attack")
def run_attack(request: AttackRequest):
    global tool
    if not tool:
        raise HTTPException(status_code=400, detail="Tool not initialized.")

    tool.configure_attack(request.intrusion_field, request.payloads)

    if request.attack_type == "html_form":
        if tool.selected_form_index is None:
            raise HTTPException(status_code=400, detail="Form not selected for HTML form attack.")
        results = tool.run_html_form_attack()

    elif request.attack_type == "api":
        if not request.api_endpoint or not request.base_body:
            raise HTTPException(status_code=400, detail="API endpoint and base body required for API attack.")
        results = tool.run_api_attack(
            method="post",
            endpoint=request.api_endpoint,
            base_body=request.base_body,
            intrusion_key=request.intrusion_field,
            payloads=request.payloads,
            headers=request.headers
        )

    elif request.attack_type == "urlencoded":
        if not request.api_endpoint or not request.param_name:
            raise HTTPException(status_code=400, detail="API endpoint and param name required for URL-encoded attack.")
        results = tool.run_urlencoded_attack(
            method="post",
            endpoint=request.api_endpoint,
            param_name=request.param_name,
            payloads=request.payloads,
            headers=request.headers
        )

    else:
        raise HTTPException(status_code=400, detail="Unknown attack type.")

    return {"results": results}
