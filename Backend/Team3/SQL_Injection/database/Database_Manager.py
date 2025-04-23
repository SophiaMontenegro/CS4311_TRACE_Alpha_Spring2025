from neo4j import GraphDatabase

class Database_Manager:
    def __init__(self, env):
        information = env.get_config()

        uri = str(information["uri"])
        user = str(information["user"])
        password = str(information["password"])
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None, fetch=False):
        """
        Runs a Cypher query with optional parameters.
        If `fetch=True`, it returns the results as a list of dictionaries.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result] if fetch else None

    def create_node(self, label, properties):
        """
        Generic method to create a node with a given label and properties.
        Example: create_node("User", {"id": 1, "name": "Alice"})
        """
        query = f"CREATE (n:{label} $props) RETURN n"
        return self.run_query(query, {"props": properties}, fetch=True)

    def create_relationship(self, label1, prop1, label2, prop2, rel_type):
        """
        Creates a relationship between two nodes based on their properties.
        Example: create_relationship("User", {"name": "Alice"}, "Project", {"id": 1}, "OWNS")
        """
        query = f"""
            MATCH (a:{label1} $props1), (b:{label2} $props2)
            MERGE (a)-[:{rel_type}]->(b)
        """
        self.run_query(query, {"props1": prop1, "props2": prop2})

    def get_nodes(self, label, filters=None):
        """
        Retrieves nodes of a specific type with optional filtering.
        Example: get_nodes("User", {"name": "Alice"})
        """
        query = f"MATCH (n:{label})"
        if filters:
            query += " WHERE " + " AND ".join([f"n.{key} = ${key}" for key in filters])
        query += " RETURN n"
        return self.run_query(query, filters, fetch=True)

    def get_projects(self, owner_initials=None):
        """
        Fetches projects, optionally filtering by owner initials.
        """
        query = """
            MATCH (u:User)-[:OWNS]->(p:Project)
            RETURN u.name AS owner, p.name AS project
        """
        if owner_initials:
            query = query.replace("RETURN", "WHERE u.name STARTS WITH $owner_initials RETURN")
        return self.run_query(query, {"owner_initials": owner_initials} if owner_initials else {}, fetch=True)

    def create_user(self, name, user_id):
        """
        Creates a user if they don’t already exist.
        """
        return self.create_node("User", {"id": int(user_id), "name": name})

    def create_project(self, owner_name, project_name, project_id):
        """
        Creates a project and assigns ownership to a user.
        """
        owner = self.get_nodes("User", {"name": owner_name})
        if not owner:
            print(f"Error: Owner '{owner_name}' not found. Please create the Lead Analyst first.")
            return

        self.create_node("Project", {"id": int(project_id), "name": project_name})
        self.create_relationship("User", {"name": owner_name}, "Project", {"id": int(project_id)}, "OWNS")
        print(f"Project '{project_name}' created and assigned to {owner_name}.")
