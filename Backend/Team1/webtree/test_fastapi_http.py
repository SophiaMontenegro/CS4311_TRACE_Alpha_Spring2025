from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional
from Team1.httpclient.http_client import HTTPClient
from Team1.httpclient.proxy_server import ProxyServer
from Team1.webtree.tree_controller import WebTreeController
from Team1.webtree.tree_builder import WebTreeBuilder

# Define the JSON schema for the Intruder Component
class IntruderRequestModel(BaseModel):
    target_url: str
    attack_type: str
    headers: Optional[dict] = None
    payloads: Optional[str] = None
    injection_points: Optional[str] = None
    hide_status_codes: Optional[str] = None
    show_only_status_codes: Optional[str] = None
    proxy: Optional[str] = None
    additional_parameters: Optional[str] = None
    operation: Optional[str] = None  # New field for operations (start, pause, restart, stop, modify)

# Define the JSON schema for the HTTP Tester Component
class HTTPTesterRequestModel(BaseModel):
    target_url: str
    http_method: str
    headers: Optional[dict] = None
    cookies: Optional[str] = None
    hide_status_codes: Optional[str] = None
    show_only_status_codes: Optional[str] = None
    proxy: Optional[str] = None
    request_body: Optional[str] = None
    additional_parameters: Optional[str] = None
    operation: Optional[str] = None  # New field for operations (start, pause, restart, stop, modify)

# Initialize FastAPI app, ProxyServer, and HTTPClient
app = FastAPI()
proxy = ProxyServer()
client = HTTPClient(proxy)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate controller
tree_builder = WebTreeBuilder(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="chrischris21"
)
controller = WebTreeController(tree_builder)

@app.post("/api/tree/update")
async def update_node_severity(payload: dict):
    ip = payload.get("ip")
    path = payload.get("path")
    severity = payload.get("severity")


    if not path or not severity:
        raise HTTPException(status_code=400, detail="Missing data")

    update_data = {
        "ip": ip,
        "path": path,
        "severity": severity
    }

    result = controller.process_tree_update(update_data)
    return {"status": "updated", "result": result}

@app.post("/intruder")
async def intruder_endpoint(request: IntruderRequestModel):
    """
    Endpoint for the Intruder Component.
    """
    # Handle operations like start, pause, restart, stop, or modify
    if request.operation:
        if request.operation == "start":
            return {"message": "Intruder operation started"}
        elif request.operation == "pause":
            return {"message": "Intruder operation paused"}
        elif request.operation == "restart":
            return {"message": "Intruder operation restarted"}
        elif request.operation == "stop":
            return {"message": "Intruder operation stopped"}
        elif request.operation == "modify":
            return {"message": "Intruder operation modified"}
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")

    # Set the target system
    if not client.specify_target_system(request.target_url):
        raise HTTPException(status_code=400, detail="Invalid target system URL.")

    # Convert JSON input to HTTP/1.1 request format
    http_request = {
        "method": "POST",  # Intruder typically uses POST requests
        "url": "/",
        "headers": request.headers or {},
        "body": request.payloads,  # Use payloads as the body
    }

    try:
        # Send the request using HTTPClient
        response = client.send_request(http_request)
        return {
            "status_code": response["status_code"],
            "headers": response["headers"],
            "body": response["body"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/http-tester")
async def http_tester_endpoint(request: HTTPTesterRequestModel):
    """
    Endpoint for the HTTP Tester Component.
    """
    # Handle operations like start, pause, restart, stop, or modify
    if request.operation:
        if request.operation == "start":
            return {"message": "HTTP Tester operation started"}
        elif request.operation == "pause":
            return {"message": "HTTP Tester operation paused"}
        elif request.operation == "restart":
            return {"message": "HTTP Tester operation restarted"}
        elif request.operation == "stop":
            return {"message": "HTTP Tester operation stopped"}
        elif request.operation == "modify":
            return {"message": "HTTP Tester operation modified"}
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")

    # Set the target system
    if not client.specify_target_system(request.target_url):
        raise HTTPException(status_code=400, detail="Invalid target system URL.")

    # Convert JSON input to HTTP/1.1 request format
    http_request = {
        "method": request.http_method,
        "url": "/",
        "headers": request.headers or {},
        "body": request.request_body,
    }

    try:
        # Send the request using HTTPClient
        response = client.send_request(http_request)
        return {
            "status_code": response["status_code"],
            "headers": response["headers"],
            "body": response["body"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

def test_fastapi_endpoint():
    """
    Simulate requests to the FastAPI app using TestClient.
    """
    test_client = TestClient(app)

    # Test the Intruder Component with a start operation
    intruder_request = {
        "target_url": "https://juice-shop.herokuapp.com",
        "attack_type": "Sniper",
        "headers": {"Content-Type": "application/json"},
        "payloads": "?id=, ?username",
        "injection_points": "?id=, ?username",
        "hide_status_codes": "403",
        "show_only_status_codes": "200, 500",
        "proxy": "https://proxy.example.com:3128",
        "additional_parameters": None,
        "operation": "start"  # Example operation
    }
    intruder_response = test_client.post("/intruder", json=intruder_request)

    # Print detailed response for the Intruder Component
    print("\n--- Intruder Component Response ---")
    print("Response Status Code:", intruder_response.status_code)
    print("Response Headers:", intruder_response.headers)
    print("Response Body:", intruder_response.json())

    # Test the HTTP Tester Component with a start operation
    http_tester_request = {
        "target_url": "https://juice-shop.herokuapp.com",
        "http_method": "GET",
        "headers": {"Content-Type": "application/json"},
        "cookies": "csrf_token=abc123",
        "hide_status_codes": "403",
        "show_only_status_codes": "200, 500",
        "proxy": "https://proxy.example.com:3128",
        "request_body": None,
        "additional_parameters": None,
        "operation": "start"  # Example operation
    }
    http_tester_response = test_client.post("/http-tester", json=http_tester_request)

    # Print detailed response for the HTTP Tester Component
    print("\n--- HTTP Tester Component Response ---")
    print("Response Status Code:", http_tester_response.status_code)
    print("Response Headers:", http_tester_response.headers)
    print("Response Body:", http_tester_response.json())

def test_http_client_direct():
    """
    Directly test HTTPClient with a raw request.
    """
    client.specify_target_system("https://juice-shop.herokuapp.com")
    raw_request = {
        "method": "GET",
        "url": "/",
        "headers": {
            "User-Agent": "TestClient",
            "Accept": "application/json"
        },
        "body": None
    }
    response = client.send_request(raw_request)

    # Print detailed response for the direct HTTPClient test
    print("\n--- Direct HTTPClient Response ---")
    print("Response Status Code:", response["status_code"])
    print("Response Headers:", response["headers"])
    print("Response Body Preview:", response["body"][:500])  # Show first 500 characters

if __name__ == "__main__":
    # Run the FastAPI endpoint tests
    test_fastapi_endpoint()

    # Run the direct HTTPClient test
    test_http_client_direct()
