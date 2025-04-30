from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse
from .tree_builder import WebTreeBuilder
from .tree_controller import WebTreeController

router = APIRouter()

tree_builder = WebTreeBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="tree-test"  # <- your password here
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
        "severity": payload.get("severity"),
        "operation": "update"
    }

    result = controller.process_tree_update(update_data)
    return {"status": "updated", "result": result}

@router.get("/webtree/dummy_tree.json")
async def get_visible_tree():
    current_tree = tree_builder.fetch_tree()
    controller_obj = WebTreeController(tree_builder)
    formatted_tree = controller_obj.build_tree_structure(current_tree)
    return formatted_tree["visible"]

@router.get("/webtree/hidden_tree.json")
async def get_hidden_tree():
    current_tree = tree_builder.fetch_tree()
    controller_obj = WebTreeController(tree_builder)
    formatted_tree = controller_obj.build_tree_structure(current_tree)
    return formatted_tree["hidden"]

# @router.post("/tree/save-static")
# async def save_static_tree():
#     tree = tree_builder.fetch_tree()
#     formatted = controller.build_tree_structure(tree)

#     # Save visible
#     with open(os.path.join(BASE_DIR, "../../../Frontend/static/webtree/dummy_tree.json"), "w") as f:
#         json.dump(formatted["visible"], f, indent=2)

#     # Save hidden
#     with open(os.path.join(BASE_DIR, "../../../Frontend/static/webtree/hidden_tree.json"), "w") as f:
#         json.dump(formatted["hidden"], f, indent=2)

#     return {"status": "saved"}

@router.post("/tree/save-static")
async def save_static_tree():
    """
    Rebuilds the dummy_tree.json and hidden_tree.json files from the current Neo4j data.
    """
    current_tree = tree_builder.fetch_tree()
    formatted = controller.build_tree_structure(current_tree)

    dummy_path = os.path.join(os.path.dirname(__file__), "../../../Frontend/static/webtree/dummy_tree.json")
    hidden_path = os.path.join(os.path.dirname(__file__), "../../../Frontend/static/webtree/hidden_tree.json")

    # Save visible nodes
    os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
    with open(dummy_path, "w", encoding="utf-8") as f:
        json.dump(formatted["visible"], f, indent=2)

    # Save hidden nodes
    os.makedirs(os.path.dirname(hidden_path), exist_ok=True)
    with open(hidden_path, "w", encoding="utf-8") as f:
        json.dump(formatted["hidden"], f, indent=2)

    return {"status": "saved"}