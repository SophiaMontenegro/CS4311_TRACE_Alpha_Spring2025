# testing/test_client.py

import requests

# === Non-hidden nodes (parents exist) ===
json_samples = [
    {"ip": "198.51.100.1", "path": "https://example.com/", "severity": "root"},
    {"ip": "198.51.100.3", "path": "https://example.com/help", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/home", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/metrics", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/settings", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/about", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team/members", "severity": "low"},

    # === Hidden nodes (parents missing or not sent yet) ===
    {"ip": "198.51.100.1", "path": "https://example.com/about/company/history", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/login/reset", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/register/validate", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/cloud/compute", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/ai/nlp", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/contact/sales", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/blog/posts/trending", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/faq/security/test", "severity": "high"}
]

# Send each JSON via POST to FastAPI
for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['path']} → {response.status_code} | {response.json()}")
