# fuzzer_response_processor.py

import json
import logging
from typing import List

class FuzzerResponseProcessor:
    """
    FuzzerResponseProcessor processes and filters HTTP responses obtained during fuzz testing.

    Attributes:
        None

    Methods:
        def __init__() -> None
        def set_filters(status_filter: List[int], hide_codes: List[int] = [], length_threshold: int = None) -> None
        def process_response(response: object) -> None
        def get_filtered_results() -> List[]

    Notes:
        The processor is intended to work with `MockResponse`-like objects having attributes: status_code, text, url, and optionally payload, error.
    """

    def __init__(self) -> None:
        self.responses = []
        self.status_code_filter = [200, 403, 500]
        self.hide_codes = []
        self.length_threshold = 0

    def set_filters(self, status_filter: List[int], hide_codes: List[int] = [], length_threshold: int = None) -> None:
        """
        set_filters sets the filtering criteria used during response processing.

        Args:
            status_filter (List[int]): Status codes to keep.
            hide_codes (List[int], ): Status codes to ignore completely.
            length_threshold ([int]): Minimum length of response body to keep.

        Returns:
            None

        Raises:
            TypeError: If any of the arguments are of an unexpected type.

        @requires isinstance(status_filter, list);
        @requires all(isinstance(code, int) for code in status_filter);
        @requires hide_codes is None or all(isinstance(code, int) for code in hide_codes);
        @requires length_threshold is None or isinstance(length_threshold, int);
        @ensures self.status_code_filter == status_filter;
        @ensures self.hide_codes == hide_codes;
        @ensures self.length_threshold == length_threshold;
        """
        self.status_code_filter = status_filter
        self.hide_codes = hide_codes
        self.length_threshold = length_threshold

    def process_response(self, response: object) -> None:
        """
        process_response analyzes and stores the response if it passes filter criteria.

        Args:
            response (object): An object with at least `status_code`, `url`, and `text`.

        Returns:
            None

        Raises:
            AttributeError: If the response lacks required attributes.
            TypeError: If response text is not a string.

        @requires hasattr(response, 'status_code') and hasattr(response, 'text') and hasattr(response, 'url');
        @requires isinstance(response.text, str);
        @ensures len(self.responses) >= 0;
        """
        status = response.status_code
        content_length = len(response.text)
        if status in self.hide_codes:
            return
        logging.info("Filtered response: %s [%d bytes]", response.url, content_length)
        if status in self.status_code_filter and content_length >= self.length_threshold:
            self.responses.append({
                "id": len(self.responses) + 1,
                "response": status,
                "url": response.url,
                "payload": getattr(response, "payload", None),
                "length": content_length,
                "snippet": response.text[:200],
                "error": getattr(response, "error", False)
            })

    def get_filtered_results(self) -> List:
        """
        get_filtered_results retrieves all responses that matched the filtering criteria.

        Args:
            None

        Returns:
            List[]: List of processed response dictionaries.

        Raises:
            None
        
        @ensures isinstance(result, list);
        """
        return self.responses