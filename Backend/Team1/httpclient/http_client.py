import requests
from urllib.parse import urlparse

class HTTPClient:
    def __init__(self, proxy_server):
        self.target_system = None
        self.history = []
        self.proxy_server = proxy_server

    def specify_target_system(self, target_system):
        """
        Ensures a valid target system URL is provided and sets it.
        Logs the action with a message indicating the target system set.
        Returns True if the target system is valid, otherwise False.
        Protocols:
        // @ requires targetSystem != null && isValidURL(targetSystem)
        // @ ensures logEntry("Target System Set: " + targetSystem);
        // @ ensures \result == true if targetSystem is valid, otherwise false
        """
        if self.is_valid_url(target_system):
            self.target_system = target_system
            print(f"Target System Set: {target_system}") # Simulate logging
            return True
        return False

    def send_request(self, request):
        """
        Sends an HTTP request to the target system.
        Ensures the request and target system are valid before sending.
        Protocols:
        // @ requires request != null && targetSystem != null
        // @ requires isValidRequest(request) && isValidURL(targetSystem)
        // @ ensures response != null && response.isReceived() == true
        """
        if request is None or self.target_system is None:
            raise ValueError("Request or target system cannot be null.")
        if not self.is_valid_request(request):
            raise ValueError("Invalid HTTP request format.")

        # Ensure HTTP/1.1 compliance
        request.setdefault("headers", {})
        request["headers"].setdefault("Host", urlparse(self.target_system).netloc)
        request["headers"].setdefault("Connection", "keep-alive")

        # Send request through proxy server
        response = self.proxy_server.forward_request(request, self.target_system)

        if response:
            self.log_activity(request, response)
            return response
        raise RuntimeError("Failed to receive a valid response.")

    def log_activity(self, request, response):
        """
        Logs the HTTP request and response details.
        Protocols:
        // @ requires request != null;
        // @ requires response != null;
        // @ ensures logEntry(request, response);
        // @ ensures logs.contains(request, response);
        """
        self.history.append((request, response))
        # print(f"Logged activity: Request={request}, Response={response}") # Simulate logging

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return all([parsed.scheme in ["http", "https"], parsed.netloc])

    def is_valid_request(self, request):
        return isinstance(request, dict) and "method" in request and "url" in request