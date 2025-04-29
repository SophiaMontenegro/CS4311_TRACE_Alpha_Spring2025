# crawler_manager.py

import json
import asyncio
import datetime
import socket
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from Team1.httpclient.http_client import HTTPClient
from Team1.httpclient.proxy_server import ProxyServer
from Team7.src.modules.crawler.crawler_response import CrawlerResponseProcessor
import aiohttp

class crawler_manager:
    """
    crawler_manager manages web crawling operations, including URL traversal, data extraction, and response processing.

    Attributes:
        None

    Methods:
        configure_crawler(target_url: str, depth: int, limit: int, user_agent: str, delay: int, proxy: str, crawl_date: str = None, crawl_time: str = None, excluded_urls: str = None) -> None:
        crawl_recursive(url: str, depth_remaining: int, parent_url: str = None) -> None:
        start_crawl() -> list:
    s
    Notes:
        - Crawling process is asynchronous.
        - Crawler respects user agent, delay, and exclusions to prevent unnecessary load on websites.
        - Processed data is stored in JSON format for further analysis.
    """

    def __init__(self):
        self.config = {}
        self.proxy = ProxyServer()
        self.http_client = HTTPClient(self.proxy)
        self.processor = CrawlerResponseProcessor()
        self.visited = set()
        self.results = []
        self.table_data = []
        self.counter = 1
        self.progress_callback = lambda url, error=None: None
        self.on_new_row = None
        self._paused = False
        self._stopped = False

    def stop(self):
        """
        Signal the crawler to stop processing further URLs.
        """
        self._stopped = True

    def pause(self):
        """
        Pauses the crawler, causing it to wait until resumed.
        """
        self._paused = True

    def resume(self):
        """
        Resumes a paused crawler
        """
        self._paused = False

    def set_progress_callback(self, callback):
        """
        Sets a callback function that will be called whenever a URL is processed.
        The callback should accept two parameters: url and error (which can be None).
        """
        self.progress_callback = callback
    
    async def send_update(self, ip: str, full_url: str, hidden: str, status_code: int, severity: int):
        """
        Sets up the call to send the responses to webtree
        """
        try:
            parsed = urlparse(full_url)
            payload = {
                "ip": ip,
                "url": full_url,
                "path": parsed.path or "/",
                "status_code": status_code,
                "hidden": hidden,
                "severity": severity,
                "operation": "update"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/api/tree/update", json=payload) as response:
                    response_text = await response.text()
                    print(f"Sent {parsed}: {response.status} - {response_text}")
        except Exception as e:
            print(f"Error sending update for {full_url}: {e}")
    
    def get_ip_from_target_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            if parsed.hostname:
                return socket.gethostbyname(parsed.hostname)
        except Exception as e:
            print(f"Failed to resolve IP for {url}: {e}")
        return "0.0.0.0"  

    def configure_crawler(self, target_url: str, depth: int, limit: int, user_agent: str, delay: int, proxy: str, crawl_date: str = None, crawl_time: str = None, excluded_urls: str = None) -> None:
        """
        configure_crawler configures the crawler with user defined settings.

        Args:
            target_url (str): The starting URL for the crawler.
            depth (int): The maximum depth of recursion for crawling.
            limit (int): The maximum number of pages to crawl.
            user_agent (str): The user agent string for the crawler's HTTP requests.
            delay (int): The delay (in milliseconds) between requests.
            proxy (str): The proxy server to use for the requests.
            crawl_date (str, optional): The date the crawl is executed, in YYYY-MM-DD format.
            crawl_time (str, optional): The time the crawl is executed, in HH:MM format.
            excluded_urls (str, optional): Comma-separated list of URLs to exclude from crawling.

        Returns:
            None

        Raises:
            None

        @requires target_url != "";
        @requires depth > 0;
        @requires limit > 0;
        @requires user_agent != "";
        @requires delay >= 0;
        @ensures config == {target_url, depth, limit, user_agent, delay, proxy, crawl_date, crawl_time, excluded_urls};
        """
        self.config = {
            "target_url": target_url,
            "depth": depth,
            "limit": limit,
            "user_agent": user_agent,
            "delay": delay,
            "proxy": proxy,
            "crawl_date": crawl_date,
            "crawl_time": crawl_time,
            "excluded_urls": excluded_urls.split(',') if excluded_urls else []
        }
        self.http_client.specify_target_system(target_url)
        # Reset flags
        self._paused = False
        self._stopped = False


    async def crawl_recursive(self, url: str, depth_remaining: int, parent_url: str = None) -> None:
        """
        crawl_recursive recursively crawls URLs while respecting depth limits and exclusions.

        Args:
            url (str): The current URL to crawl.
            depth_remaining (int): The number of remaining recursion levels.
            parent_url (str, optional): The parent URL of the current URL, for context.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the HTTP request or while processing the page.

        @requires url != "";
        @requires depth_remaining >= 0;
        @ensures visited contains url if depth_remaining >= 0;
        """
        # Check if we're paused
        while self._paused and not self._stopped:
            await asyncio.sleep(0.5)

        # Check if it was stopped
        if self._stopped:
            return
        
        if url in self.visited or depth_remaining < 0 or len(self.visited) >= self.config.get("limit", 100):
            return
            
        self.visited.add(url)
        headers = {"User-Agent": self.config.get("user_agent", "")}
        parsed = urlparse(url)
        try:
            request = {
                "method": "GET",
                "url": parsed.path or "/",
                "headers": headers 
            }
            response = self.http_client.send_request(request)
            raw_html = response["body"]
            await asyncio.sleep(self.config.get("delay", 0) / 1000.0)

            self.progress_callback(url)

            if depth_remaining == self.config.get("depth"):
                with open("Team7/src/database/crawler/raw_html.txt", "w", encoding="utf-8") as f:
                    f.write(raw_html)

            soup = BeautifulSoup(raw_html, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"
            text = soup.get_text()
            word_count = len(text.split())
            char_count = len(text)
            links_found = len(soup.find_all("a"))

            row = {
                "id": self.counter,
                "url": url,
                "parentUrl": parent_url,
                "title": title,
                "wordCount": word_count,
                "charCount": char_count,
                "linksFound": links_found,
                "error": False
            }
            
            self.table_data.append(row)

            if callable(self.on_new_row):
                self.on_new_row(row)

            self.counter += 1

            processed_result = self.processor.process_response(raw_html, base_url=url)
            self.results.append({"url": url, "data": processed_result})

            # Check for stopped before starting recursive call
            if self._stopped:
                return

            for extracted_url in processed_result.get("extracted_urls", []):
                # Check if stopped or paused before each next URL
                while self._paused and not self._stopped:
                    await asyncio.sleep(0.5)
                if self._stopped:
                    return
                
                if any(excluded in extracted_url for excluded in self.config["excluded_urls"]):
                    continue
                full_url = urljoin(url, extracted_url)
                await self.crawl_recursive(full_url, depth_remaining - 1, parent_url=url)

        except Exception as e:
            error_row = {
                "id": self.counter,
                "url": url,
                "parentUrl": parent_url,
                "title": "Error",
                "wordCount": 0,
                "charCount": 0,
                "linksFound": 0,
                "error": True
            }
            self.table_data.append(error_row)

            if callable(self.on_new_row):
                self.on_new_row(error_row)

            self.counter += 1
            self.progress_callback(url, str(e))

    async def start_crawl(self) -> list:
        """
        start_crawl initiates the crawling process and writes results to a JSON file.

        Args:
            None

        Returns:
            list: A list of processed crawl results, including extracted data from crawled pages.

        Raises:
            None

        @ensures result is a list of processed crawl results;
        """

        await self.crawl_recursive(self.config.get("target_url"), self.config.get("depth"))

        with open("Team7/src/database/crawler/crawler_table_data.json", "w", encoding="utf-8") as f:
            json.dump(self.table_data, f, indent=1)

        print("Crawling completed. Results written to crawler_table_data.json")

        target_ip = self.get_ip_from_target_url(self.config["target_url"])

        for result in self.results:
            await self.send_update(target_ip, result["url"], False , 200, 5)

        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8000/api/tree/save-static") as response:
                print("Saved static tree:", response.status)
        
        return self.results
    

# Sample test run
if __name__ == '__main__':
    manager = crawler_manager()
    manager.configure_crawler(
        target_url="https://quotes.toscrape.com/",
        depth=5,
        limit=100,
        user_agent="Mozilla/5.0",
        delay=1000,
        proxy="8080",
        crawl_date=str(datetime.date.today()),
        crawl_time="22:00",
        excluded_urls="/login,/admin"
    )

    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(manager.start_crawl())
        loop.run_until_complete(task)
    except RuntimeError:
        asyncio.run(manager.start_crawl())