# intruder_tool_full.py
# Code by erick
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import json
import csv  
import os
import uuid
from datetime import datetime


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
        
    def export_log_to_csv(self, job_id: str, mode: str, job_dir: str):
        """Export a summary log for the job inside the same job folder."""
        log_file = os.path.join(job_dir, "intruder_log.csv")

        successful = sum(1 for r in self.results if r.get("status_code") and str(r.get("status_code")).startswith("2"))
        failed = len(self.results) - successful

        with open(log_file, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "job_id", "target_url", "attack_type", "payloads_tried", "success", "failures"])
            writer.writeheader()
            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "job_id": job_id,
                "target_url": self.target_url,
                "attack_type": mode,
                "payloads_tried": len(self.results),
                "success": successful,
                "failures": failed
            })

    def export_results_to_csv(self, output_dir: str = None) -> Dict[str, str]:
        """Export detailed attack results to a CSV file inside a unique job folder."""
        if output_dir is None:
            base_dir = os.path.dirname(__file__)
            output_dir = os.path.join(base_dir, "exports")

        job_id = str(uuid.uuid4())
        job_dir = os.path.join(output_dir, job_id)

        if not os.path.exists(job_dir):
            os.makedirs(job_dir)

        results_file = os.path.join(job_dir, "intruder_results.csv")

        with open(results_file, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "payload", "status_code", "length", "error"])
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    "timestamp": datetime.now().isoformat(),
                    "payload": result.get("payload"),
                    "status_code": result.get("status_code"),
                    "length": result.get("length"),
                    "error": result.get("error")
                })

        return {"job_id": job_id, "results_file": results_file, "job_dir": job_dir}
