from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from Team1.httpclient.http_client import HTTPClient
from Team1.httpclient.proxy_server import ProxyServer

router = APIRouter()

proxy = ProxyServer()
client = HTTPClient(proxy)

@router.post("/send")
async def send_http_request(request: Request):
    try:
        data = await request.json()
        target_system = data.get("target")
        crafted_request = data.get("request")

        if not client.specify_target_system(target_system):
            raise HTTPException(status_code=400, detail="Invalid target URL")

        response = client.send_request(crafted_request)
        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/logs")
def get_http_logs():
    return {"logs": proxy.get_logs()}
