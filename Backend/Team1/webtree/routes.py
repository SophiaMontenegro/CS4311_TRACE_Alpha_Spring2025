from fastapi import APIRouter, HTTPException
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
async def update_node_severity(payload: dict):
    ip = payload.get("ip")
    path = payload.get("path")
    severity = payload.get("severity")
    status_code = payload.get("status_code")


    if not path:
        raise HTTPException(status_code=400, detail="Missing data")

    update_data = {
        "ip": ip,
        "path": path,
        "severity": severity,
        "status_code": status_code,
        "operation": "update"  # <-- Force update
    }

    result = controller.process_tree_update(update_data)
    return {"status": "updated", "result": result}

