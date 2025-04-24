# Test a single URL at a time, automatically detects mode (html/json/url)

from intruder_tool import IntruderTool
import requests
from urllib.parse import urlparse

# ------------------ Set test url below ------------------
#url = "https://httpbin.org/forms/post" 
#url = "https://reqres.in/api/users"
#url = "https://formspree.io/"
#url = "https://postman-echo.com/post"
#url = "https://www.w3schools.com/html/html_forms.asp"
#url = "https://jsonplaceholder.typicode.com/posts"
#url = "https://httpbin.org/anything"
#url = "https://api.publicapis.org/entries" #Note this is website is down which will give you "DNS resolution failed" error
#url = "https://www.formsite.com/html5/"

# Validate URL format
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except:
        return False

# Auto-detect mode based on Content-Type
def detect_mode(url: str) -> str:
    try:
        response = requests.get(url)
        content_type = response.headers.get("Content-Type", "")
        if "html" in content_type:
            return "html"
        elif "json" in content_type:
            return "json"
        else:
            return "url"  # fallback for text/plain, unknown, echo-style
    except Exception as e:
        print(f"Error detecting mode: {e}")
        return "url"

def run_html_mode(url: str):
    tool = IntruderTool(url)
    status = tool.fetch_target()
    print(f"Fetched with status: {status}")

    forms = tool.parse_forms()
    print(f"\nParsed {len(forms)} form(s).")
    if not forms:
        print("No valid forms were found on the target URL.")
        return

    print("\nAvailable Forms:")
    for i, form in enumerate(forms):
        print(f"Form {i}:")
        print(f"  Action: {form['action']}")
        print(f"  Method: {form['method']}")
        print(f"  Fields: {form['fields']}")

    tool.select_form(0)
    print("\nHTTP Request Preview:")
    print(tool.get_http_request_preview())

    tool.configure_attack(intrusion_field="custname", payloads=["123456", "admin123", "password"])
    print("\nRunning HTML form attack...")
    results = tool.run_html_form_attack()
    print("\nAttack Results:")
    for result in results:
        print(result)

def run_api_mode(url: str):
    tool = IntruderTool(url)
    print("\nRunning API-based attack...")

    preview = {
        "url": url,
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "sample_body": {"name": "<payload>", "job": "engineer"}
    }
    print("\nHTTP Request Preview:")
    print(preview)

    results = tool.run_api_attack(
        method="POST",
        endpoint=url,
        base_body={"name": "placeholder", "job": "engineer"},
        intrusion_key="name",
        payloads=["123456", "admin123", "password"]
    )

    print("\nAPI Attack Results:")
    for result in results:
        print(result)


def run_url_mode(url: str):
    tool = IntruderTool(url)
    print("\nRunning URL-encoded attack...")

    preview = {
        "url": url,
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "form_body": {"input": "<payload>"}
    }
    print("\nHTTP Request Preview:")
    print(preview)

    results = tool.run_urlencoded_attack(
        method="POST",
        endpoint=url,
        param_name="input",
        payloads=["123456", "admin123", "password"]
    )

    print("\nGeneric URL Attack Results:")
    for result in results:
        print(result)


# ======= MAIN RUNNER =======

if not is_valid_url(url):
    print("Invalid URL format. Must start with http:// or https://")
    exit(1)

mode = detect_mode(url)
print(f"\nDetected mode: {mode}")
print(f"Target URL: {url}")

if mode == "html":
    run_html_mode(url)
elif mode == "json":
    run_api_mode(url)
elif mode == "url":
    run_url_mode(url)
else:
    print("Unsupported or undetectable mode.")
