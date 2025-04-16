import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from typing import List
import csv
import os 
import urllib.parse
#import aiofiles

class WebScraper:
    """
    Asynchronous web scraper to extract text content from web pages,
    including logos, labels, and class titles.

    Attributes:
        urls (list): List of URLs to scrape.
        concurrency (int): Maximum number of concurrent connections.

    Methods:
        scrape_pages(self, filename: str="scraped_output.csv") -> None

        async _fetch_url(self, url: str) -> str

        _extract_text_content(self, html: str) -> str

        async _scrape_pages_async(self) -> List
    """
    
    def __init__(self, urls: List, concurrency: int=5):
        """
        Initialize with list of URLs and optional concurrency limit.
        
        Args:
            urls (list): List of URLs to scrape.
            concurrency (int): Max number of parallel fetches.
        """
        self.urls = urls
        self.concurrency = concurrency
        self.filename = None
        

    async def scrape_pages(self, filename: str="scraped_output.csv")->None:
        """
        Public main method to run the async scraping from sync code.
        """
        data = await self._scrape_pages_async()

        # Save the results
        # TODO: Update the path to the database folder.
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write a header for clarity
            csv_writer.writerow(['id', 'content', 'url'])
            csv_writer.writerows(data)
        print(f'[INFO] CSV file {filename} has been generated.')
        self.filename = filename
        return filename

    async def _fetch_url(self, url: str) -> str:
        """
        Fetch the HTML content of a single URL asynchronously.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The raw HTML text is successful, or an empty string if an error occurs.
        """
        # TODO: Update to fetch the URLs from the database.
        """
        try:
            async with aiofiles.open(url, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            print(f"[ERROR] Could not fetch {url}")
            return ""
        """
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme == "file":
            local_path = os.path.normpath(parsed_url.path)
            try:
                # TODO: Update the path to the database folder.
                with open(local_path, "r", encoding="utf-8") as f:
                    return f.read()
                
            except Exception as e:
                print(f"[ERROR] Could not open local file: {e}")
                return ""
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.text()
            except aiohttp.ClientError as e:
                print(f"[ERROR] Could not fetch {url}: {e}")
                return ""
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
        """

    def _extract_text_content(self, html: str) -> str:
        """
        Parse the HTML and extract:
            - Text from <p>, <h1>, <h2>, <h3>, <span>
            - Logos: text from images (often used for logos).
            - Labels: text that is listed inside labels.
            - Class titles: any CSS class attributes from elements.

        Args:
            html (str): the HTML content to parse.
        
        Returns:
            str: A combined string of extracted text.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Gather textual content from standard text tags
        text_parts = []
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'label', 'div', 'section', 'main', 'li', 'lu' ]):
            text_parts.append(tag.get_text(strip=True))
            
        # Gather "logo" text from <img alt="..">
        for img in soup.find_all("img"):
            alt_text = img.get("alt")
            if alt_text:
                text_parts.append(alt_text)

        # Gather aria-label or aria-labelledby attribues
        # aria-labelledby is an ID reference, so we do a basic attempt to extract it
        for element in soup.find_all(attrs={"aria-label": True}):
            text_parts.append(element.get("aria-label"))
        for element in soup.find_all(attrs={"aria-labelledby": True}):
            label_id = element.get('aria-labelledby')
            if label_id:
                ref = soup.find(id=label_id)
                if ref and ref.text:
                    text_parts.append(ref.text.strip())
        
        # Gather class attributes from all elements
        for el in soup.find_all(attrs={'class': True}):
            class_attr = el.get('class')
            # class_attr might be a list of classes; join them
            if class_attr and isinstance(class_attr, list):
                text_parts.append(" ".join(class_attr))

        # Merge everything into one string
        return " ".join(part for part in text_parts if part)
    

    async def _scrape_pages_async(self) -> List:
        """
        Asynchronoulsy scrape text content from all URLs in self.urls.

        Args:
            None

        Returns:
            list of tuples: [(id, content, url), ...]
        """
        results = []
        sem = asyncio.Semaphore(self.concurrency)

        async with aiohttp.ClientSession() as session:
            async def scrape_page(i, url):
                async with sem:
                    html = await self._fetch_url(url)
                    if html:
                        text_content = self._extract_text_content(html)
                    else:
                        text_content = ""
                    results.append((i, text_content, url))

            tasks = []
            for i, url in enumerate(self.urls, start=1):
                tasks.append(scrape_page(i, url))

            await asyncio.gather(*tasks)

        # Sort the final results by ID
        results.sort(key=lambda x: x[0])
        return results
    
    
        print(f"CSV file '{filename}' has been generated.")
