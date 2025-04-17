import os
import time
import logging
import asyncio
from typing import List, Dict, Callable, Optional
from Team1.httpclient.proxy_server import ProxyServer
from Team1.httpclient.http_client import HTTPClient
from Team7.src.modules.dbf.dbf_response_processor import ResponseProcessor
# TODO: add the new http client

log_path = os.path.join(os.path.dirname(__file__), "directory_bruteforce.log")
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

class DirectoryBruteForceManager:
    def __init__(self) -> None:
        self.config = {}
        self.response_processor = ResponseProcessor()
        # TODO: add the new http client
        self.proxy = ProxyServer()
        self.http_client = HTTPClient(self.proxy)
        self.request_count = 0
        self.attempt_limit = -1
        self.start_time = None
        self.end_time = None
        self._paused = False
        self._stopped = False
        self.wordlist = []
        self.current_index = 0
        self.on_new_row = None

    def configure_scan(
        self,
        target_url: str,
        wordlist: List[str],
        top_dir: str = '',
        hide_status: List[int] = None,
        show_only_status: List[int] = None,
        length_filter: int = None,
        headers: Dict[str, str] = None,
        attempt_limit: int = -1
    ) -> None:
        if not target_url or not wordlist:
            raise ValueError("Missing required configuration parameters.")

        self.config = {
            "target_url": target_url.rstrip('/'),
            "wordlist": wordlist,
            "top_dir": top_dir.strip('/'),
            "hide_status": hide_status or [],
            "show_only_status": show_only_status or [],
            "length_filter": length_filter,
            "headers": headers or {}
        }
        self.wordlist = wordlist
        self.attempt_limit = attempt_limit
        self.response_processor.set_filters(show_only_status or [200], hide_status or [], length_filter)
        self.http_client.specify_target_system(target_url)
        
        # Reset control flags
        self._paused = False
        self._stopped = False
        self.current_index = 0

    async def start_scan(self) -> None:
        self.start_time = time.perf_counter()
        target = self.config["target_url"]
        top = self.config["top_dir"]
        wordlist = self.config["wordlist"]
        headers = self.config["headers"]

        for i, word in enumerate(wordlist):
            self.current_index = i
            
            while self._paused and not self._stopped:
                await self._wait_pause()
                
            # Check if we should stop after pause
            if self._stopped:
                logging.info("Scan stopped after pause.")
                break
                
            path = f"{top}/{word}" if top else word
            full_url = f"{target}/{path}"
            try:
                request = {
                    "method": "GET",
                    "url": f"/{path.lstrip('/')}",
                    "headers": headers
                }
                response = self.http_client.send_request(request)
                mock = MockResponse(full_url, response["status_code"], response["body"])
                mock.payload = word
                mock.error = response["status_code"] not in [200, 403]
                self.response_processor.process_response(mock)
                
                # Create a result object that can be sent to frontend
                result_item = {
                    "id": self.request_count + 1,
                    "url": full_url,
                    "status": response["status_code"],
                    "payload": word,
                    "length": len(response["body"]),
                    "error": mock.error
                }
                
                # Call the callback if it exists
                if callable(self.on_new_row):
                    self.on_new_row(result_item)
                    
                logging.info("Scanned %s [%d]", full_url, response["status_code"])
                self.request_count += 1
            except Exception as e:
                logging.error("Request error for %s: %s", full_url, str(e))
                error_response = MockResponse(full_url, 0, str(e))
                error_response.payload = word
                error_response.error = True
                self.response_processor.process_response(error_response)
                
                # Create an error result object
                error_item = {
                    "id": self.request_count + 1,
                    "url": full_url,
                    "status": 0,
                    "payload": word,
                    "length": 0,
                    "error": True
                }
                
                # Call the callback if it exists
                if callable(self.on_new_row):
                    self.on_new_row(error_item)
                    
                self.request_count += 1
        
        # Set end time if not stopped
        if not self._stopped:
            self.end_time = time.perf_counter()
        else:
            self.end_time = time.perf_counter()

    async def _wait_pause(self, interval=0.5):
        """Helper method to wait during pause state"""
        await asyncio.sleep(interval)

    def pause(self):
        """Pause the scanning process"""
        self._paused = True
        logging.info("Pausing scan at word index %d", self.current_index)

    def resume(self):
        """Resume a paused scan"""
        self._paused = False
        logging.info("Resuming scan from word index %d", self.current_index)

    def stop(self):
        """Stop the scanning process"""
        self._stopped = True
        logging.info("Stopping scan at word index %d", self.current_index)
        # Set end time when stopping
        if not self.end_time:
            self.end_time = time.perf_counter()

    def get_metrics(self) -> Dict[str, float]:
        current_time = time.perf_counter()
        total_time = (self.end_time or current_time) - (self.start_time or current_time) if self.start_time else 0
        rps = self.request_count / total_time if total_time > 0 else 0
        return {
            "running_time": total_time,
            "processed_requests": self.request_count,
            "filtered_requests": len(self.response_processor.get_filtered_results()),
            "requests_per_second": rps
        }

    def get_filtered_results(self) -> List[Dict]:
        """Get the filtered results from the response processor"""
        filtered_results = self.response_processor.get_filtered_results()
        
        # Add id field if not present
        for i, result in enumerate(filtered_results):
            if 'id' not in result:
                result['id'] = i + 1
                
        return filtered_results
    
    def save_results_to_txt(self, filename: str = "dbf_results.txt") -> None:
        results = self.get_filtered_results()
        # TODO: Update the path to the database folder.
        with open(filename, "w", encoding="utf-8") as f:
            for entry in results:
                f.write(f"URL: {entry['url']}\n")
                f.write(f"Status: {entry['status']}\n")
                f.write(f"Payload: {entry['payload']}\n")
                f.write(f"Length: {entry['length']}\n")
                f.write(f"Error: {entry['error']}\n")
                f.write("-" * 40 + "\n")

#sample test
if __name__ == '__main__':
    manager = DirectoryBruteForceManager()

    # Sample wordlist
    wordlist = [
        '',  # root
        'level1/page1',
        'level1/page2',
        'level2/page1',
        'level2/page2',
        'level2/page3',
        'notfound'
    ]

    # Configure the scan
    manager.configure_scan(
        target_url='http://localhost:5002',
        wordlist=wordlist,
        hide_status=[404],
        show_only_status=[200],
        length_filter=0,
        attempt_limit=-1
    )

    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(manager.start_scan())
        loop.run_until_complete(task)
    except RuntimeError:
        asyncio.run(manager.start_scan())