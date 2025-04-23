import json
from neo4j import GraphDatabase

class WebTreeBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """ Closes the database connection. """
        self.driver.close()

    def fetch_tree(self):
        """ Fetches the full tree structure from Neo4j. """
        with self.driver.session() as session:
            result = session.run("MATCH (n:Node) RETURN n.path AS path, n.severity AS severity, n.ip AS ip, n.hidden AS hidden")
            tree = [{
                "path": r["path"],
                "severity": r["severity"],
                "ip": r.get("ip", "0.0.0.0"),
                "hidden": r.get("hidden", False)
            } for r in result]

        return tree
    
    def process_update(self, json_data):
        """
        Processes the JSON input, creates or updates nodes, and ensures proper parent-child relationships.
        Assigns severity internally if not provided.
        """
        try:
            data = json.loads(json_data)
            node_path = data.get("path")
            ip_address = data.get("ip", None)
            status_code = data.get("status_code")
            hidden = data.get("hidden", False)

            severity = data.get("severity") or self.assign_severity(node_path, ip_address)
            operation = data.get("operation")

            # === Re-validate parent path for adding/updating ===
            if node_path == "/":
                parent_path = None
            elif node_path.count("/") == 1:
                parent_path = "/"
            else:
                parent_path = "/".join(node_path.split("/")[:-1])

            # === Apply operation ===
            if operation == "add":
                self.add_node(node_path, severity, parent_path, ip_address, status_code, data.get("url"), hidden)
            elif operation == "update":
                self.update_node(node_path, severity, ip_address, status_code, data.get("url"), hidden)

            # === Confirm changes ===
            updated_tree = self.fetch_tree()
            print("Updated Tree Sent to Controller:", updated_tree)
            return updated_tree

        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
            return None
        
    def add_node(self, path, severity, parent_path=None, ip=None, status_code=None, url=None, hidden=False):
        with self.driver.session() as session:
            # Always ensure the root node `/` exists
            session.run(
                """
                MERGE (n:Node {path: $path})
                ON CREATE SET 
                    n.severity = $severity, 
                    n.ip = $ip, 
                    n.status_code = $status_code, 
                    n.url = $url,
                    n.hidden = $hidden
                """,
                path=path, severity=severity, ip=ip, status_code=status_code, url=url, hidden=hidden
            )


            # Determine parent if not explicitly given
            if path == "/":
                parent_path = None
            elif not parent_path:
                parent_path = "/" if path.count("/") == 1 else "/".join(path.split("/")[:-1])

            # Create or merge the actual node
            session.run(
                """
                MERGE (n:Node {path: $path})
                ON CREATE SET n.severity = $severity, n.ip = $ip
                """,
                path=path, severity=severity, ip=ip
            )

            # If node has a parent (and it’s not root itself), ensure parent exists
            if parent_path and parent_path != "/":
                session.run(
                    """
                    MERGE (parent:Node {path: $parent_path})
                    ON CREATE SET parent.severity = "unknown", parent.ip = "0.0.0.0"
                    """,
                    parent_path=parent_path
                )

            # Link to parent (including making `/home` a child of `/`)
            if parent_path:
                session.run(
                    """
                    MATCH (child:Node {path: $path})
                    MATCH (parent:Node {path: $parent_path})
                    MERGE (child)-[:CHILD_OF]->(parent)
                    """,
                    path=path, parent_path=parent_path
                )

            print(f"Node {path} added (Parent: {parent_path if parent_path else 'None'})")

    def update_node(self, path, severity, ip=None, status_code=None, url=None, hidden=False):
        """ Updates an existing node's severity and status code. """
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n:Node {path: $path})
                SET n.severity = $severity,
                    n.ip = $ip,
                    n.status_code = $status_code,
                    n.url = $url,
                    n.hidden = $hidden
                """,
                path=path, severity=severity, ip=ip, status_code=status_code, url=url, hidden=hidden
            )
        print(f"Node updated: {path} | severity: {severity} | status_code: {status_code}")


    def assign_severity(self, path, ip):
        path = path.lower() if path else ""
        if any(keyword in path for keyword in ["admin", "login", "reset", "root"]):
            return "high"
        elif any(keyword in path for keyword in ["dashboard", "settings", "config"]):
            return "medium"
        else:
            return "low"

    def update_severity(self, path, severity):
        with self.driver.session() as session:
            query = """
            MATCH (n {path: $path})
            SET n.severity = $severity
            RETURN n
            """
            session.run(query, path=path, severity=severity)
            print(f"Severity updated for {path} to {severity}")
    
    def status_code_to_severity(self, code):
        try:
            code = int(code)
        except:
            return "unknown"

        if code == 200:
            return "high"
        elif code in [401, 403, 405, 500, 302, 301]:
            return "medium"
        elif code in [400, 503]:
            return "low"
        return "unknown"
