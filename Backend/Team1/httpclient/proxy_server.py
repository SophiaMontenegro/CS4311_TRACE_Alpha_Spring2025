import time
import requests

class ProxyServer:
    def __init__(self):
        self.logs = []
        self.session = requests.Session()

    def forward_request(self, request, target_system):
        """
        Forwards the request and returns a dict including:
         - status_code
         - headers
         - body
         - time    ← elapsed milliseconds
         - size    ← response body size in bytes
         - error   ← error message if an exception occurs
        """
        if not target_system or not request:
            err = "Target system and request cannot be null."
            self.logs.append(err)
            return {"error": err, "time": None, "size": None}

        self.logs.append(f"\n\nCaptured Request:\n {request}")

        start = time.time()
        try:
            resp = self.session.request(
                method=request.get("method"),
                url=f"{target_system}{request.get('url')}",
                headers=request.get("headers", {}),
                data=request.get("body", None),
                allow_redirects=True,
                stream=True,
                verify=True
            )
        except requests.RequestException as e:
            elapsed = int((time.time() - start) * 1000)
            err_msg = f"Error forwarding request: {e}"
            self.logs.append(err_msg)
            return {"error": err_msg, "time": elapsed, "size": None}
        end = time.time()

        # Read full body to compute size
        try:
            content = resp.content
            body_text = content.decode(resp.encoding or "utf-8", errors="replace")
            size_bytes = len(content)
        except Exception as e:
            body_text = resp.text if hasattr(resp, 'text') else ''
            size_bytes = None
            self.logs.append(f"Error reading body: {e}")

        time_ms = int((end - start) * 1000)

        response_data = {
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "body": body_text,
            "time": time_ms,
            "size": size_bytes
        }

        self.logs.append(f"\n\nCaptured Response:\n {response_data}")
        return response_data

    def get_logs(self):
        return self.logs