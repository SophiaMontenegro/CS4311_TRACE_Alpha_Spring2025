# manual_test_intruder.py
from intruder_tool import IntruderTool

# Set your test URL here
# url = "https://httpbin.org/forms/post" 
# url = "https://reqres.in/api/users"
# url = "https://formspree.io/"
# url = "https://postman-echo.com/post"
# url = "https://www.w3schools.com/html/html_forms.asp"
url = "https://jsonplaceholder.typicode.com/posts"
# url = "https://httpbin.org/anything"
# url = "https://api.publicapis.org/entries"
# url = "https://www.formsite.com/html5/"
# url = "https://juice-shop.herokuapp.com"

# Step 1: Create the tool
tool = IntruderTool(url)

# Step 2: Validate the URL using the instance
if not tool.is_valid_url():
    print("Invalid URL format. Must start with http:// or https://")
    exit(1)

# Step 3: Detect the mode
mode = tool.detect_mode()
print(f"\nDetected mode: {mode}")
print(f"Target URL: {url}")

# Step 4: Run based on mode
if mode == "html":
    status = tool.fetch_target()
    print(f"Fetched status: {status}")
    forms = tool.parse_forms()

    if not forms:
        print("No forms detected.")
        exit(1)

    tool.select_form(0)
    print("\nHTTP Request Preview:")
    print(tool.get_http_request_preview())

    tool.configure_attack(
        intrusion_field="custname",  # adjust if the form has different fields
        payloads=["123456", "admin", "admin123"]
    )

    print("\nRunning HTML Form Attack...")
    results = tool.run_html_form_attack()

elif mode == "json":
    print("\nRunning API Attack...")
    results = tool.run_api_attack(
        method="POST",
        endpoint=url,
        base_body={"name": "placeholder", "job": "engineer"},
        intrusion_key="name",
        payloads=["123456", "admin", "admin123"]
    )

elif mode == "url":
    print("\nRunning URL-Encoded Attack...")
    results = tool.run_urlencoded_attack(
        method="POST",
        endpoint=url,
        param_name="input",  # key for URL-encoded param
        payloads=["123456", "admin", "admin123"]
    )

else:
    print("Unsupported or undetectable mode.")
    exit(1)

# Step 5: Print results
print("\nAttack Results:")
for result in results:
    print(result)
