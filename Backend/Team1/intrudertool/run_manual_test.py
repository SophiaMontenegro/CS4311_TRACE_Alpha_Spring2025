# run_manual_test.py

from intruder_tool import IntruderTool

# Step 1: Define the target URL
tool = IntruderTool("https://httpbin.org/forms/post")

# Step 2: Fetch the page
status = tool.fetch_target()
print(f"Fetched with status: {status}")

# Step 3: Parse forms on the page
forms = tool.parse_forms()
print(f"\nParsed {len(forms)} form(s).")
if not forms:
    print("No valid forms were found on the target URL.")
    exit()

# Step 4: Show form details
print("\nAvailable Forms:")
for i, form in enumerate(forms):
    print(f"Form {i}:")
    print(f"  Action: {form['action']}")
    print(f"  Method: {form['method']}")
    print(f"  Fields: {form['fields']}")

# Step 5: Select form index (default to first form)
tool.select_form(0)

# Step 6: Preview the HTTP request structure
print("\nHTTP Request Preview:")
print(tool.get_http_request_preview())

# Step 7: Define intrusion field and payloads
tool.configure_attack(intrusion_field="custname", payloads=["123456", "admin123", "password"])

# Step 8–11: Run the attack and show results
print("\nRunning attack...")
results = tool.run_attack()

print("\nAttack Results:")
for result in results:
    print(result)
