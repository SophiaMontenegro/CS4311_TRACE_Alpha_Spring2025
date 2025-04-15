import requests

class ProxyServer:
    def __init__(self):
        self.logs = []
        self.session = requests.Session()  # Maintain persistent connections

    def forward_request(self, request, target_system):
        """
        Forwards the request to the target system and returns the response.
        Ensures the target system and request are valid and that the target system has a response.
        Protocols:
        // @ requires targetSystem != null;
        // @ requires request != null;
        // @ requires targetSystem.hasResponse(request);
        // @ ensures response != null;
        // @ ensures httpClient.receiveResponse(response);
        """
        if not target_system or not request:
            raise ValueError("Target system and request cannot be null.")

        # Capture incoming request
        self.logs.append(f"\n\nCaptured Request:\n {request}")

        try:
            response = self.session.request(
                method=request.get("method"),
                url=f"{target_system}{request.get('url')}",
                headers=request.get("headers", {}),
                data=request.get("body", None),
                allow_redirects=True,  # Handle redirects automatically
                stream=True,  # Enable chunked streaming
                verify=True  # Ensure SSL verification
            )

            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000]  # Limit response size in logs
            }
            self.logs.append(f"\n\nCaptured Response:\n {response_data}")

            return response_data
        except requests.RequestException as e:
            raise RuntimeError(f"Error forwarding request: {e}")

    def get_logs(self):
        return self.logs
