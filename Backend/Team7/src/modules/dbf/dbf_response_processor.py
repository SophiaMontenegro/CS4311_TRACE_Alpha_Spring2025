import json

class ResponseProcessor:
    def __init__(self, response=None):
        self.response = response or []
    
    def process_response(self, response):
        self.response.append({
            "url": response.url,
            "status": response.status_code,
            "payload": response.payload,
            "length": len(response.text),
            "error": response.error
        })

    def set_filters(self, status_filter, hide_codes=None, length_threshold=None):
        self.status_code_filter = status_filter
        self.hide_codes = hide_codes or []
        self.length_threshold = length_threshold or 0

    def filter_by_status(self, status_codes):
        return [r for r in self.response if r.get("status") in status_codes]

    def filter_by_content_length(self, min_len=0, max_len=float('inf')):
        return [r for r in self.response if min_len <= r.get("length", 0) <= max_len]

    def extract_successful(self):
        return [r for r in self.response if r.get("status") and 200 <= r["status"] < 300]

    def log_results(self):
        for res in self.response:
            print(f"[{res.get('status', 'ERROR')}] {res['url']} (len={res.get('length', 0)})")
            if res.get('error'):
                print(f"  ↳ Error: {res['error']}")
    
    def get_filtered_results(self):
        filtered = []

        for res in self.response:
            status = res.get("status")
            length = res.get("length", 0)

            # Apply show_only filter
            if self.status_code_filter and status not in self.status_code_filter:
                continue

            # Apply hide_status filter
            if self.hide_codes and status in self.hide_codes:
                continue

            # Apply content length filter
            if self.length_threshold and length < self.length_threshold:
                continue

            filtered.append(res)

        return filtered



    
    
