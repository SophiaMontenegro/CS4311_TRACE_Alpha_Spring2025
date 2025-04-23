import requests

# === Sample input with new expected keys ===
json_samples = [
    {"ip": "198.51.100.1", "url": "https://example.com/", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.3", "url": "https://example.com/help", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/home", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/home/dashboard", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/home/dashboard/metrics", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/admin", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/.env", "status_code": "200", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/profile/edit", "status_code": "403", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/account/settings", "status_code": "403", "hidden": False},
    {"ip": "198.51.100.1", "url": "https://example.com/about/company/history", "status_code": "503", "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset", "status_code": "401", "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/register/validate", "status_code": "200", "hidden": True}
]

# Send each JSON via POST to FastAPI
for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['url']} → {response.status_code} | {response.json()}")
