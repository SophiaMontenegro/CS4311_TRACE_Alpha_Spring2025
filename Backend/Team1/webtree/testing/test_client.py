import requests

# json_samples = [
#     {"ip": "198.51.100.1", "url": "https://example.com/", "response_code": 200},
#     {"ip": "198.51.100.1", "url": "https://example.com/home", "response_code": 200},
#     {"ip": "198.51.100.1", "url": "https://example.com/home/dashboard", "response_code": 403},
#     {"ip": "198.51.100.1", "url": "https://example.com/about/team", "response_code": 401},

#     # Hidden subtree
#     {"ip": "198.51.100.1", "url": "https://example.com/login/reset", "response_code": 200, "hidden": True},
#     {"ip": "198.51.100.1", "url": "https://example.com/login/reset/2fa", "response_code": 403, "hidden": True},
#     {"ip": "198.51.100.1", "url": "https://example.com/login/reset/2fa/help", "response_code": 200, "hidden": True},
#     {"ip": "198.51.100.1", "url": "https://example.com/register/validate", "response_code": 200, "hidden": True}
# ]

json_samples = [
    # Root and main sections
    {"ip": "198.51.100.1", "url": "https://example.com/", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/home", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/home/dashboard", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/home/settings", "response_code": 403},
    {"ip": "198.51.100.1", "url": "https://example.com/about", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/about/team", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/about/careers", "response_code": 404},
    {"ip": "198.51.100.1", "url": "https://example.com/contact", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/contact/support", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/contact/feedback", "response_code": 200},

    # Services Section
    {"ip": "198.51.100.1", "url": "https://example.com/services", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/services/consulting", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/services/development", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/services/development/web", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/services/development/mobile", "response_code": 200},

    # Blog section
    {"ip": "198.51.100.1", "url": "https://example.com/blog", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/blog/news", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/blog/events", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/blog/releases", "response_code": 200},
    {"ip": "198.51.100.1", "url": "https://example.com/blog/releases/v1.0", "response_code": 200},

    # Hidden login/reset subtree
    {"ip": "198.51.100.1", "url": "https://example.com/login", "response_code": 200, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset", "response_code": 403, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset/password", "response_code": 403, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset/2fa", "response_code": 403, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/login/reset/2fa/help", "response_code": 200, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/register", "response_code": 200, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/register/validate", "response_code": 200, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/register/verify-email", "response_code": 200, "hidden": True},
    {"ip": "198.51.100.1", "url": "https://example.com/profile/settings", "response_code": 401},
    {"ip": "198.51.100.1", "url": "https://example.com/profile/security", "response_code": 401}
]


for entry in json_samples:
    response = requests.post("http://localhost:8000/api/tree/update", json=entry)
    print(f"Sent: {entry['url']} → {response.status_code} | {response.json()}")
