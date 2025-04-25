# fuzzer_manager.py

import os
import time
import logging
from typing import List, Dict, Any, Callable
import asyncio
from urllib.parse import urlparse
from Team1.httpclient.http_client import HTTPClient
from Team1.httpclient.proxy_server import ProxyServer
from Team7.src.modules.fuzzer.fuzzer_response_processor import FuzzerResponseProcessor

log_path = os.path.join(os.path.dirname(__file__), "fuzzing.log")
logging.basicConfig(
    filename=log_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MockResponse:
    def __init__(self, url: str, status: int, text: str):
        self.url = url
        self.status_code = status
        self.text = text
        self.payload = None
        self.error = False

class FuzzerManager:
    """
    FuzzerManager manages configuration and execution of HTTP fuzzing sessions.

    Attributes:
        None

    Methods:
        configure_fuzzing(...) -> None
        start_fuzzing() -> Coroutine
        get_metrics() -> Dict[str, [int, float]]
        get_filtered_results() -> List[Dict]

    Notes:
        Use this class to automate black box fuzz testing of web applications or APIs.
    """

    def __init__(self) -> None:
        self.config = {}
        self.response_processor = FuzzerResponseProcessor()
        self.proxy = ProxyServer()
        self.http_client = HTTPClient(self.proxy)
        self.request_count = 0
        self.start_time = None
        self.end_time = None
        self._paused = False
        self._stopped = False
        self.progress_callback = None
        self.on_new_row = None
        self.last_row = None

    def set_progress_callback(self, callback: Callable):
        """
        Sets a callback function that will be called whenever a request is processed.
        """
        self.progress_callback = callback

    def stop(self):
        """
        Signal the fuzzer to stop processing further requests.
        """
        self._stopped = True

    def pause(self):
        """
        Pauses the fuzzer, causing it to wait until resumed.
        """
        self._paused = True

    def resume(self):
        """
        Resumes a paused fuzzer
        """
        self._paused = False

    def configure_fuzzing(
        self,
        target_url: str,
        http_method: str,
        headers: Dict = None,
        cookies: Dict = None,
        proxy: str = None,
        body_template: Dict = None,
        parameters: List[str] = None,
        payloads: List[str] = None
    ) -> None:
        """
        configure_fuzzing accepts and stores the configuration required for the fuzzing session.

        Args:
            target_url (str): URL to send requests to.
            http_method (str): HTTP method (GET, POST).
            headers ([Dict]): HTTP headers.
            cookies ([Dict]): HTTP cookies.
            proxy ([str]):  proxy URL.
            body_template ([Dict]): Template for request body.
            parameters (List[str]): List of parameters to fuzz.
            payloads ([str, List[str]]): Payloads or path to file containing them.

        Returns:
            None

        Raises:
            ValueError: If any required argument is missing or invalid.

        @requires target_url is not None and target_url != "";
        @requires http_method is not None and http_method != "";
        @requires parameters is not None and len(parameters) > 0;
        @requires payloads is not None and (isinstance(payloads, list) or os.path.isfile(payloads));
        @ensures "target_url" in self.config and self.config["target_url"] == target_url;
        @ensures isinstance(self.config["payloads"], list) and len(self.config["payloads"]) > 0;
        """
        if not target_url or not http_method or not parameters or not payloads:
            raise ValueError("Missing required fuzzing configuration parameters.")
        if isinstance(payloads, str) and os.path.isfile(payloads):
            with open(payloads, "r", encoding="utf-8") as f:
                payloads = [line.strip() for line in f if line.strip()]
        if not isinstance(payloads, list) or not payloads:
            raise ValueError("Payloads must be a non-empty list or a valid file path.")
        self.config = {
            "target_url": target_url,
            "http_method": http_method,
            "headers": headers or {},
            "cookies": cookies or {},
            "proxy": proxy,
            "body_template": body_template or {},
            "parameters": parameters,
            "payloads": payloads
        }
        self.http_client.specify_target_system(target_url)

        # Reset status flags
        self._paused = False
        self._stopped = False
        self.request_count = 0

        self.processed_ids = set()

    async def start_fuzzing(self) -> None:
        self.start_time = time.perf_counter()
        """
        start_fuzzing begins fuzzing by sending requests using the provided configuration.
        Sends HTTP requests for every parameter and payload combination, then processes the responses using the response processor.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: If a request fails unexpectedly during fuzzing.

        @requires self.config is not None and all required keys are present;
        @ensures self.request_count >= 0;
        @ensures self.end_time >= self.start_time;
        """
        target_url = self.config.get("target_url")
        http_method = self.config.get("http_method", "GET").upper()
        headers = self.config.get("headers", {})
        cookies = self.config.get("cookies", {})
        proxy = self.config.get("proxy")
        body_template = self.config.get("body_template", {})
        parameters = self.config.get("parameters", [])
        payloads = self.config.get("payloads", [])
        logging.info(f"Fuzzing started with {len(payloads)} payloads across {len(parameters)} parameter(s)")
        proxies = {"http": proxy, "https": proxy} if proxy else None
        parsed = urlparse(target_url)
        for payload in payloads:
            # Check if paused or stopped
            while self._paused and not self._stopped:
                await asyncio.sleep(0.5)
            if self._stopped:
                logging.info(f'Fuzzing stopped after {self.request_count} requests')
                break

            for param in parameters:
                # Check if paused or stopped
                while self._paused and not self._stopped:
                    await asyncio.sleep(0.5)
                if self._stopped:
                    logging.info(f'Fuzzing stopped after {self.request_count} requests')
                    break

                modified_body = body_template.copy()
                modified_body[param] = payload
                logging.info(f"Sending {http_method} request to {target_url} with {param}={payload}")
                try:
                    request = {
                        "method": http_method,
                        "url": parsed.path or "/",
                        "headers": headers
                    }
                    if http_method in ["POST", "PUT"]:
                        request["body"] = modified_body
                    response = self.http_client.send_request(request)
                    await asyncio.sleep(0.3)
                    mock = MockResponse(target_url, response["status_code"], response["body"])
                    mock.payload = payload
                    mock.error = response["status_code"] not in [200]

                    # Convert this into a table row format
                    row = {
                        "id": self.request_count + 1,
                        "url": target_url,
                        "response": response["status_code"],
                        "payload": payload,
                        "length": len(response["body"]),
                        "error": mock.error
                    }

                    # Emit the row immediately
                    if callable(self.on_new_row):
                        self.last_row = row
                        self.on_new_row(row)
                        time.sleep(0.3)

                    self.response_processor.process_response(mock)

                    logging.info(f'Recieve response {response['status_code']} from {target_url}')
                    self.request_count += 1
                    
                    total_count = len(parameters) * len(payloads)
                    self.progress_callback(self.request_count, total_count, f'{param}={payload}')
                except Exception as e:
                    print(f"[!] Request error {e}")
                    error_response = MockResponse(target_url, 0, str(e))
                    error_response.payload = payload
                    error_response.error = True

                    error_row = {
                        "id": self.request_count + 1,
                        "url": target_url,
                        "response": 0,
                        "payload": payload,
                        "length": len(str(e)),
                        "error": True
                    }

                    if callable(self.on_new_row):
                        self.last_row = error_row
                        self.on_new_row(error_row)

                    self.response_processor.process_response(error_response)
        self.end_time = time.perf_counter()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        get_metrics returns performance metrics for the fuzzing session.

        Args:
            None

        Returns:
            Dict[str, [int, float]]: Metrics including total time, request count,
            filtered request count, and requests per second.

        Raises:
            None
        
        @ensures result["running_time"] >= 0;
        @ensures result["processed_requests"] == self.request_count;
        @ensures result["filtered_requests"] >= 0;
        """
        total_time = self.end_time - self.start_time if self.start_time and self.end_time else 0
        rps = self.request_count / total_time if total_time > 0 else 0
        return {
            "running_time": total_time,
            "processed_requests": self.request_count,
            "filtered_requests": len(self.response_processor.get_filtered_results()),
            "requests_per_second": rps
        }
    
    def get_filtered_results(self) -> List[Dict]:
        """
        get_filtered_results returns the filtered results of the fuzzing session.

        Args:
            None

        Returns:
            List[Dict]: List of responses that matched filter criteria.

        Raises:
            None
        
        @ensures isinstance(result, list);
        """
        return self.response_processor.get_filtered_results()