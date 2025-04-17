from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse
from .tree_builder import WebTreeBuilder
from .tree_controller import WebTreeController

router = APIRouter()

tree_builder = WebTreeBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password=""
)
controller = WebTreeController(tree_builder)

@router.post("/update")
async def update_node(payload: dict):
    ip = payload.get("ip")
    url = payload.get("url")
    response_code = payload.get("response_code")
    hidden = payload.get("hidden", False)

    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    parsed = urlparse(url)
    path = parsed.path or "/"

    update_data = {
        "ip": ip,
        "url": url,
        "path": path,
        "status_code": response_code,
        "hidden": hidden,
        "operation": "update"
    }

    result = controller.process_tree_update(update_data)
    return {"status": "updated", "result": result}