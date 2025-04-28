# intruder_tool_full.py
# Code by erick
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import json

class IntruderTool:
    """
    Main Intruder Tool class.
    Handles HTML form attacks, API JSON payload attacks, and URL-encoded attacks.
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
        try:
            response = requests.get(self.target_url)
            self.html = response.text
            return response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Fetch failed: {self._shorten_error(e)}")
            self.html = ""
            return -1

    def parse_forms(self) -> List[Dict]:
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
        if index >= len(self.forms) or index < 0:
            raise IndexError("Selected form index is out of range.")
        self.selected_form_index = index

    def get_http_request_preview(self) -> Dict:
        form = self.forms[self.selected_form_index]
        full_action_url = urljoin(self.target_url, form["action"])
        return {
            "url": full_action_url,
            "method": form["method"],
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "sample_body": {field["name"]: "<value>" for field in form["fields"] if field["name"]}
        }

    def configure_attack(self, intrusion_field: str, payloads: List[str]):
        self.intrusion_field = intrusion_field
        self.payloads = payloads

    def run_html_form_attack(self) -> List[Dict]:
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
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": 0,
                    "error": short_error
                })

        return self.results

    def run_api_attack(self, method: str, endpoint: str, base_body: Dict, intrusion_key: str,
                       payloads: List[str], headers: Optional[Dict] = None) -> List[Dict]:
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
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": 0,
                    "error": short_error
                })

        return self.results

    def run_urlencoded_attack(self, method: str, endpoint: str, param_name: str,
                              payloads: List[str], headers: Optional[Dict] = None) -> List[Dict]:
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
                self.results.append({
                    "payload": payload,
                    "status_code": None,
                    "length": len(short_error),
                    "error": short_error
                })

        return self.results

    def _shorten_error(self, e: Exception) -> str:
        full_msg = str(e)
        if "Failed to resolve" in full_msg:
            return "DNS resolution failed"
        if "Max retries exceeded" in full_msg:
            return "Server unreachable (max retries)"
        if "Connection refused" in full_msg:
            return "Connection refused"
        return full_msg.split(":")[0]

    def detect_mode(self) -> str:
        try:
            response = requests.get(self.target_url)
            content_type = response.headers.get("Content-Type", "")
            body = response.text

            if "json" in content_type:
                return "json"
            elif "html" in content_type:
                return "html"

            # Try parsing body to detect JSON
            try:
                json.loads(body)
                return "json"
            except Exception:
                pass

            return "url"
        except Exception as e:
            print(f"Error detecting mode: {e}")
            return "url"

    def is_valid_url(self, url: Optional[str] = None) -> bool:
        """
        Validate if a URL is properly formatted.
        If no URL is provided, validates the tool's target_url.
        """
        check_url = url or self.target_url
        try:
            result = urlparse(check_url)
            return all([result.scheme in ["http", "https"], result.netloc])
        except:
            return False
