# run_manual_test.py
# Simple tester for one URL, now saves results and logs properly

from intruder_tool import IntruderTool
import requests
from urllib.parse import urlparse
import json

# ------------- Set your test URL below -------------
#url = "https://httpbin.org/forms/post"  # Change this to the URL you want to test
#url = "https://reqres.in/api/users"
#url = "https://formspree.io/"
#url = "https://postman-echo.com/post"
url = "https://www.w3schools.com/html/html_forms.asp"
#url = "https://jsonplaceholder.typicode.com/posts"
#url = "https://httpbin.org/anything"
#url = "https://api.publicapis.org/entries" #Note this is website is down which will give you "DNS resolution failed" error
#url = "https://www.formsite.com/html5/"
#url = "https://juice-shop.herokuapp.com"

attack_strategy = "Sniper"
payloads = ["123456", "admin123", "password"]
intrusion_field_default = "custname"

# ------------- Helper Functions -------------

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except:
        return False

def detect_mode(url: str) -> str:
    try:
        response = requests.get(url)
        content_type = response.headers.get("Content-Type", "")
        if "html" in content_type:
            return "html"
        elif "json" in content_type:
            return "json"
        else:
            return "url"
    except Exception as e:
        print(f"Error detecting mode: {e}")
        return "url"

# ------------- Mode Runners -------------

def run_html_mode(url: str):
    print("\nRunning HTML form attack...")
    tool = IntruderTool(url)
    status = tool.fetch_target()

    if status == -1:
        print("Failed to fetch target. Exiting HTML mode.")
        return

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
    preview = tool.get_http_request_preview()
    print("\nHTTP Request Preview:")
    print(json.dumps(preview, indent=2))

    tool.configure_attack(intrusion_field=intrusion_field_default, payloads=payloads)
    results = tool.run_html_form_attack()

    print("\nAttack Results:")
    for result in results:
        print(result)

    export_info = tool.export_results_to_csv()
    tool.export_log_to_csv(export_info["job_id"], "html", export_info["job_dir"])

def run_api_mode(url: str):
    print("\nRunning API-based attack...")
    tool = IntruderTool(url)
    status = tool.fetch_target()

    if status == -1:
        print("Failed to fetch target. Exiting API mode.")
        return

    preview = {
        "url": url,
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "sample_body": {"name": "<payload>", "job": "engineer"}
    }
    print("\nHTTP Request Preview:")
    print(json.dumps(preview, indent=2))

    results = tool.run_api_attack(
        method="POST",
        endpoint=url,
        base_body={"name": "placeholder", "job": "engineer"},
        intrusion_key="name",
        payloads=payloads
    )

    print("\nAPI Attack Results:")
    for result in results:
        print(result)

    export_info = tool.export_results_to_csv()
    tool.export_log_to_csv(export_info["job_id"], "json", export_info["job_dir"])

def run_url_mode(url: str):
    print("\nRunning URL-encoded attack...")
    tool = IntruderTool(url)
    status = tool.fetch_target()

    if status == -1:
        print("Failed to fetch target. Exiting URL mode.")
        return

    preview = {
        "url": url,
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "form_body": {"input": "<payload>"}
    }
    print("\nHTTP Request Preview:")
    print(json.dumps(preview, indent=2))

    results = tool.run_urlencoded_attack(
        method="POST",
        endpoint=url,
        param_name="input",
        payloads=payloads
    )

    print("\nGeneric URL Attack Results:")
    for result in results:
        print(result)

    export_info = tool.export_results_to_csv()
    tool.export_log_to_csv(export_info["job_id"], "url", export_info["job_dir"])

# ------------- Main Runner -------------

if not is_valid_url(url):
    print("Invalid URL format.")
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
