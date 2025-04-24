import requests

json_samples = [
    {"ip": "198.51.100.1", "url": "https://example.com/", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/home", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/home/dashboard", "response_code": 403},
    {"ip": "198.51.100.1", "url": "https://example.com/about/team", "response_code": 401},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset", "response_code": 200, "hidden": True}
]

for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['url']} → {response.status_code} | {response.json()}")
