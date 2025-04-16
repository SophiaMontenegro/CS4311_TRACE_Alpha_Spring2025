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
            result = session.run("MATCH (n:Node) RETURN n.path AS path, n.severity AS severity, n.ip AS ip")
            tree = [{"path": r["path"], "severity": r["severity"], "ip": r.get("ip", "0.0.0.0")} for r in result]
        return tree
    
    def process_update(self, json_data):
        """
        Processes the JSON input, creates or updates nodes, and ensures proper parent-child relationships.
        """
        try:
            data = json.loads(json_data)
            node_path = data.get("path")
            severity = data.get("severity", "unknown")  # Default severity if missing
            operation = data.get("operation")
            ip_address = data.get("ip", None)

            # Determine parent path correctly
            if node_path == "/":  
                parent_path = None  # Root has no parent
            elif node_path.count("/") == 1:
                parent_path = "/"  # First-level nodes should attach to `/`
            else:
                parent_path = "/".join(node_path.split("/")[:-1])  # Normal hierarchy

            # Create or update the node
            if operation == "add":
                self.add_node(node_path, severity, parent_path, ip_address)
            elif operation == "update":
                self.update_node(node_path, severity, ip_address)

            # Fetch updated tree to confirm changes
            updated_tree = self.fetch_tree()
            print("Updated Tree Sent to Controller:", updated_tree)
            return updated_tree

        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
            return None

        
    def add_node(self, path, severity, parent_path=None, ip=None):
        with self.driver.session() as session:
            # Always ensure the root node `/` exists
            session.run(
                """
                MERGE (root:Node {path: "/"})
                ON CREATE SET root.severity = "unknown", root.ip = "0.0.0.0"
                """
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



    def update_node(self, path, severity, ip=None):
        """ Updates an existing node's severity. """
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n:Node {path: $path})
                SET n.severity = $severity, n.ip = $ip
                """,
                path=path, severity=severity, ip=ip
            )
        print(f"Node updated: {path}")

    def update_severity(self, path, severity):
        with self.driver.session() as session:
            query = """
            MATCH (n {path: $path})
            SET n.severity = $severity
            RETURN n
            """
            session.run(query, path=path, severity=severity)
            print(f"Severity updated for {path} to {severity}")