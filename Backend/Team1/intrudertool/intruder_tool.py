# intruder_tool.py
# Clean version with short error logging

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional

class IntruderTool:
    """
    The main class for the Intruder Tool.
    Handles HTML form attacks, JSON API payloads, and generic URL-based payloads.
    """

    def __init__(self, target_url: str):
        self.target_url = target_url
        self.html = ""
        self.forms = []
        self.selected_form_index = None
        self.payloads = []
        self.intrusion_field = ""
        self.results = []

    def fetch_target(self) -> int:
        """
        Fetch the HTML content of the target URL.
        Returns the HTTP status code, or -1 if the request fails.
        """
        try:
            response = requests.get(self.target_url)
            self.html = response.text
            return response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Fetch failed: {self._shorten_error(e)}")
            self.html = ""
            return -1

    def parse_forms(self) -> List[Dict]:
        """
        Parse the HTML to identify forms containing input fields.
        Returns a list of form metadata with actions, methods, and input fields.
        """
        soup = BeautifulSoup(self.html, "html.parser")
        for form in soup.find_all("form"):
            fields = [{"name": f.get("name"), "type": f.get("type")} for f in form.find_all("input")]
            if form.find_all("input"):
                self.forms.append({
                    "action": form.get("action", ""),
                    "method": form.get("method", "get").lower(),
                    "fields": fields
                })
        return self.forms

    def select_form(self, index: int):
        """
        Select a form to target based on its index in the forms list.
        """
        if index >= len(self.forms) or index < 0:
            raise IndexError("Selected form index is out of range.")
        self.selected_form_index = index

    def get_http_request_preview(self) -> Dict:
        """
        Generate a preview of what the HTTP request would look like for the selected form.
        """
        form = self.forms[self.selected_form_index]
        full_action_url = urljoin(self.target_url, form["action"])
        return {
            "url": full_action_url,
            "method": form["method"],
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "sample_body": {field["name"]: "<value>" for field in form["fields"] if field["name"]}
        }

    def configure_attack(self, intrusion_field: str, payloads: List[str]):
        """
        Define the field to inject payloads into and provide the payload list.
        """
        self.intrusion_field = intrusion_field
        self.payloads = payloads

    def run_html_form_attack(self) -> List[Dict]:
        """
        Execute the attack loop by sending payloads to the selected HTML form.
        Returns a list of results including status code and response length.
        """
        form = self.forms[self.selected_form_index]
        action_url = urljoin(self.target_url, form["action"])
        method = form["method"]
        self.results = []

        for payload in self.payloads:
            form_data = {
                f["name"]: "admin" for f in form["fields"]
                if f["name"] and f["name"] != self.intrusion_field
            }
            form_data[self.intrusion_field] = payload

            try:
                if method == "post":
                    response = requests.post(action_url, data=form_data)
                else:
                    response = requests.get(action_url, params=form_data)
                self.results.append({
                    "payload": payload,
                    "status_code": response.status_code,
                    "length": len(response.text)
                })
            except requests.exceptions.RequestException as e:
                short_error = self._shorten_error(e)
                print(f"Request failed for '{payload}': {short_error}")
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": 0,
                    "error": short_error
                })

        return self.results

    def run_api_attack(self, method: str, endpoint: str, base_body: Dict, intrusion_key: str,
                       payloads: List[str], headers: Optional[Dict] = None) -> List[Dict]:
        """
        Run payload injection on an API endpoint that accepts JSON.
        """
        self.results = []
        headers = headers or {"Content-Type": "application/json"}

        for payload in payloads:
            body = base_body.copy()
            body[intrusion_key] = payload

            try:
                if method.lower() == "post":
                    response = requests.post(endpoint, json=body, headers=headers)
                elif method.lower() == "get":
                    response = requests.get(endpoint, params=body, headers=headers)
                else:
                    raise ValueError("Unsupported HTTP method for API attack.")
                self.results.append({
                    "payload": payload,
                    "status_code": response.status_code,
                    "length": len(response.text)
                })
            except requests.exceptions.RequestException as e:
                short_error = self._shorten_error(e)
                print(f"Request failed for '{payload}': {short_error}")
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": 0,
                    "error": short_error
                })

        return self.results

    def run_urlencoded_attack(self, method: str, endpoint: str, param_name: str,
                              payloads: List[str], headers: Optional[Dict] = None) -> List[Dict]:
        """
        Run generic URL-encoded attack against endpoints that accept raw form data.
        """
        self.results = []
        headers = headers or {"Content-Type": "application/x-www-form-urlencoded"}

        for payload in payloads:
            data = {param_name: payload}

            try:
                if method.lower() == "post":
                    response = requests.post(endpoint, data=data, headers=headers)
                elif method.lower() == "get":
                    response = requests.get(endpoint, params=data, headers=headers)
                else:
                    raise ValueError("Unsupported HTTP method.")
                self.results.append({
                    "payload": payload,
                    "status_code": response.status_code,
                    "length": len(response.text)
                })
            except requests.exceptions.RequestException as e:
                short_error = self._shorten_error(e)
                print(f"Request failed for '{payload}': {short_error}")
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": 0,
                    "error": short_error
                })

        return self.results

    def _shorten_error(self, e: Exception) -> str:
        """
        Utility method to extract a short, readable message from an exception.
        """
        full_msg = str(e)
        if "Failed to resolve" in full_msg:
            return "DNS resolution failed"
        if "Max retries exceeded" in full_msg:
            return "Server unreachable (max retries)"
        if "Connection refused" in full_msg:
            return "Connection refused"
        return full_msg.split(":")[0]  # fallback: just the first part
