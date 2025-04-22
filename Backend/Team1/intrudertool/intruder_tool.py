# intruder_tool.py
# Code by erick
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict

class IntruderTool:
    """
    The main class for the Intruder Tool.
    Handles form discovery, selection, payload injection, and attack execution.
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
        Returns the HTTP status code.
        """
        response = requests.get(self.target_url)
        self.html = response.text
        return response.status_code

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
        Generate a preview of what the HTTP request would look like
        for the selected form with placeholder values.
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

    def run_attack(self) -> List[Dict]:
        """
        Execute the attack loop by sending payloads to the selected form.
        Returns the results of each payload attempt.
        """
        form = self.forms[self.selected_form_index]
        action_url = urljoin(self.target_url, form["action"])
        method = form["method"]

        for payload in self.payloads:
            form_data = {
                f["name"]: "admin" for f in form["fields"]
                if f["name"] and f["name"] != self.intrusion_field
            }
            form_data[self.intrusion_field] = payload

            if method == "post":
                response = requests.post(action_url, data=form_data)
            else:
                response = requests.get(action_url, params=form_data)

            self.results.append({
                "payload": payload,
                "status_code": response.status_code,
                "length": len(response.text)
            })

        return self.results