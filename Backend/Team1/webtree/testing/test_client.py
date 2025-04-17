# testing/test_client.py

import requests

# === Non-hidden nodes (parents exist) ===
json_samples = [
    {"ip": "198.51.100.1", "path": "https://example.com/", "status_code": "200"},
    {"ip": "198.51.100.3", "path": "https://example.com/help", "status_code": "200"},
    {"ip": "198.51.100.1", "path": "https://example.com/home", "status_code": "200"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard", "status_code": "200"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/metrics", "status_code": "200"},

    # === High severity from path, status_code irrelevant
    {"ip": "198.51.100.1", "path": "https://example.com/admin", "status_code": "200"},
    {"ip": "198.51.100.1", "path": "https://example.com/.env", "status_code": "200"},

    # === Medium severity from path
    {"ip": "198.51.100.1", "path": "https://example.com/profile/edit", "status_code": "403"},
    {"ip": "198.51.100.1", "path": "https://example.com/account/settings", "status_code": "403"},

    # === Hidden nodes, status_code used for severity
    {"ip": "198.51.100.1", "path": "https://example.com/about/company/history", "status_code": "503"},  # → low
    {"ip": "198.51.100.1", "path": "https://example.com/login/reset", "status_code": "401"},            # → medium
    {"ip": "198.51.100.1", "path": "https://example.com/register/validate", "status_code": "200"}       # → high
]


# Send each JSON via POST to FastAPI
for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['path']} → {response.status_code} | {response.json()}")