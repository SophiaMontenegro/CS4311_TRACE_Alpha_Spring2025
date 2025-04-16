# crawler_response.py

from bs4 import BeautifulSoup

class Node:
    """
    Node represents a node in a tree structure, containing a value, left and right child references, and a list of children.

    Attributes:
        None

    Methods:
        None

    Notes:
        None
    """

    def __init__(self, value) -> None:
        self.value = value
        self.left = None
        self.right = None
        self.children = []

class BST:
    """
    BST is responsible for managing a tree structure of nodes. It supports insertion of nodes, building a tree from a list of URLs, and saving the tree structure to a file.

    Attributes:
        None
    
    Methods:
        insert(parent: Node, value: str) -> Node:
        build_tree(root_url: str, children: list[str]) -> None:
        _write_tree(node: Node, depth: int, lines: list[str]) -> None:
            A helper function to recursively write the tree structure to a list of strings.
        save_tree_to_file(filename: str) -> None:
        
    Notes:
        None
    """

    def __init__(self) -> None:
        self.root = None
        self.node_map = {}

    def insert(self, parent: Node, value: str) -> Node:
        """
        insert inserts a new node with the given value into the tree, attaching it as a child of the specified parent node.

        Args:
            parent (Node): The parent node to which the new node will be attached.
            value (str): The value to be stored in the new node.

        Returns:
            Node: The newly created node.

        Raises:
            None

        @requires value != "";
        @ensures a new node is inserted into the tree with the given value, and is linked to the parent node if provided.
        """
        if value in self.node_map:
            return self.node_map[value]
        new_node = Node(value)
        self.node_map[value] = new_node
        if parent:
            parent.children.append(new_node)
        if not self.root:
            self.root = new_node
        return new_node

    def build_tree(self, root_url: str, children: list[str]) -> None:
        """
        build_tree builds a tree with the given root URL and a list of child URLs.

        Args:
            root_url (str): The URL to be used as the root of the tree.
            children (list[str]): A list of child URLs to be inserted under the root URL.

        Returns:
            None

        Raises:
            None

        @requires root_url != "";
        @requires all elements of children are non-empty strings;
        @ensures a tree is built with the root URL and its children URLs.
        """
        root_node = self.insert(None, root_url)
        for url in children:
            self.insert(root_node, url)

    def _write_tree(self, node: Node, depth: int, lines: list[str]) -> None:
        """
        _write_tree recursively writes the tree structure to a list of strings.

        Args:
            node (Node): The current node to be written.
            depth (int): The current depth of the node in the tree.
            lines (list[str]): The list of strings where the tree structure will be written.

        Returns:
            None

        Raises:
            None

        @requires node != None;
        @ensures tree structure is recursively written to the list of strings.
        """
        if node:
            lines.append("  " * depth + node.value)
            for child in node.children:
                self._write_tree(child, depth + 1, lines)

    def save_tree_to_file(self, filename: str) -> None:
        """
        save_tree_to_file saves the tree structure to a file.

        Args:
            filename (str): The name of the file where the tree structure will be saved.

        Returns:
            None

        Raises:
            None

        @requires filename != "";
        @ensures tree structure is saved to the specified file.
        """
        lines = []
        self._write_tree(self.root, 0, lines)
        with open(filename, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

class CrawlerResponseProcessor:
    """
    CrawlerResponseProcessor processes the raw HTML content from a webpage, extracts URLs, and organizes them in a binary search tree (BST) structure for further analysis and storage.

    Attributes:
       None

    Methods:
        process_response(raw_html: str, base_url: str = "") -> dict:
            
    Notes:
        None
    """

    def __init__(self) -> None:
        self.bst = BST()

    def process_response(self, raw_html: str, base_url: str = "") -> dict:
        """
        process_response processes the raw HTML content to extract all the relevant URLs and store them in the BST.

        Args:
            raw_html (str): The raw HTML content of the page.
            base_url (str, optional): The base URL of the page to link the extracted URLs.

        Returns:
            dict: A dictionary containing the name of the processor, a sorted list of extracted URLs from the page, and the count of unique extracted URLs.

        Raises:
            None

        @requires raw_html != "";
        @requires base_url != "" if raw_html contains URLs;
        @ensures returns a dictionary containing processor info, sorted URLs, and their count.
        """
        soup = BeautifulSoup(raw_html, "html.parser")
        urls = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            if not href.startswith("mailto:") and not href.startswith("#"):
                urls.add(href)
        for tag in soup.find_all("link", href=True):
            urls.add(tag["href"])
        for tag in soup.find_all("script", src=True):
            urls.add(tag["src"])
        for tag in soup.find_all("img", src=True):
            urls.add(tag["src"])
        for tag in soup.find_all("form", action=True):
            urls.add(tag["action"])
        self.bst.build_tree(base_url, urls)
        self.bst.save_tree_to_file("extracted_urls_tree.txt")
        return {"processor": "CrawlerResponseProcessor", "extracted_urls": sorted(list(urls)),
            "count": len(urls),}