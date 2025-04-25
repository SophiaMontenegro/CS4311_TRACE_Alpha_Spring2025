from urllib.parse import urlparse

class HTTPClient:
    def __init__(self, proxy_server):
        """
        :param proxy_server: an instance of ProxyServer (or any object with .forward_request())
        """
        self.target_system = None
        self.history = []
        self.proxy_server = proxy_server

    def specify_target_system(self, target_system):
        """
        Set the base URL of the system you want to target.
        Returns True if the URL is valid and was set; False otherwise.
        """
        if self.is_valid_url(target_system):
            self.target_system = target_system
            print(f"Target System Set: {target_system}")
            return True
        return False

    def send_request(self, request):
        """
        Send an HTTP request (dict with keys 'method', 'url', optional 'headers' & 'body')
        through the configured proxy_server. Returns either:
          - a dict with status_code, statusText, headers, body, time, size
          - or {'error': '...'} on validation/network failure
        """
        # 1) Pre-validate inputs
        if request is None or self.target_system is None:
            return {"error": "Request or target system cannot be null."}
        if not self.is_valid_request(request):
            return {"error": "Invalid HTTP request format."}

        # 2) Ensure HTTP/1.1 compliance headers
        request.setdefault("headers", {})
        request["headers"].setdefault("Host", urlparse(self.target_system).netloc)
        request["headers"].setdefault("Connection", "keep-alive")

        try:
            # 3) Forward via the proxy
            resp = self.proxy_server.forward_request(request, self.target_system)

            # 4) If proxy reported an error, log & return it
            if resp.get("error"):
                self.log_activity(request, resp)
                return {"error": resp["error"]}

            # 5) Otherwise log success and normalize the payload
            self.log_activity(request, resp)
            return {
                "status_code": resp["status_code"],
                "statusText": resp.get("headers", {}).get("Status", ""),
                "headers": resp["headers"],
                "body": resp["body"],
                "time": resp["time"],
                "size": resp["size"],
            }

        except Exception as e:
            # 6) Catch any unexpected exception, record it, and return as error
            err_msg = str(e)
            self.history.append((request, {"error": err_msg}))
            return {"error": err_msg}

    def log_activity(self, request, response):
        """
        Append the (request, response) tuple to this client's history.
        """
        self.history.append((request, response))

    def is_valid_url(self, url):
        """
        Basic URL validation: must have http/https and a netloc.
        """
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)

    def is_valid_request(self, request):
        """
        A valid request must be a dict containing at least 'method' and 'url'.
        """
        return isinstance(request, dict) and "method" in request and "url" in request
