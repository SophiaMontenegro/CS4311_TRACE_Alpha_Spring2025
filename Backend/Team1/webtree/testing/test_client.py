# testing/test_client.py

import requests

# === Non-hidden nodes (parents exist) ===
json_samples = [
    {"ip": "198.51.100.1", "path": "https://example.com/"},
    {"ip": "198.51.100.3", "path": "https://example.com/help"},
    {"ip": "198.51.100.1", "path": "https://example.com/home"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/metrics"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/settings"},
    {"ip": "198.51.100.1", "path": "https://example.com/about"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team/members"},

    # === Hidden nodes (parents missing or not sent yet) ===
    {"ip": "198.51.100.1", "path": "https://example.com/about/company/history"},
    {"ip": "198.51.100.1", "path": "https://example.com/login/reset"},
    {"ip": "198.51.100.1", "path": "https://example.com/register/validate"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/cloud/compute"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/ai/nlp"},
    {"ip": "198.51.100.1", "path": "https://example.com/contact/sales"},
    {"ip": "198.51.100.1", "path": "https://example.com/blog/posts/trending"},
    {"ip": "198.51.100.1", "path": "https://example.com/faq/security/test"}
]

# Send each JSON via POST to FastAPI
for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['path']} → {response.status_code} | {response.json()}")