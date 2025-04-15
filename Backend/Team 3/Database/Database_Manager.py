from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv
import os

class Database_Manager:
    def __init__(self):
        load_dotenv()

        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise ValueError("Missing Neo4j environment variables")

        self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None, fetch=False):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result] if fetch else None

    def create_node(self, label, properties):
        query = f"CREATE (n:{label} $props) RETURN n"
        return self.run_query(query, {"props": properties}, fetch=True)

    def create_relationship(self, label1, prop1, label2, prop2, rel_type):
        query = f"""
            MATCH (a:{label1} {{name: $props1.name}}), (b:{label2} {{id: $props2.id}})
            MERGE (a)-[:{rel_type}]->(b)
        """
        self.run_query(query, {"props1": prop1, "props2": prop2})

    def get_nodes(self, label, filters=None):
        query = f"MATCH (n:{label})"
        if filters:
            query += " WHERE " + " AND ".join([f"n.{key} = ${key}" for key in filters])
        query += " RETURN n"
        return self.run_query(query, filters, fetch=True)

    def get_projects(self, owner_initials=None):
        query = """
            MATCH (u:Analyst)-[:OWNS]->(p:Project)
            RETURN u.name AS owner, p.name AS project
        """
        if owner_initials:
            query = query.replace("RETURN", "WHERE u.name STARTS WITH $owner_initials RETURN")
        return self.run_query(query, {"owner_initials": owner_initials} if owner_initials else {}, fetch=True)

    def create_user(self, name, user_id):
        return self.create_node("Analyst", {"id": int(user_id), "name": name})

    def create_project(self, owner_name, project_name, project_id, timeline, description):
        owner = self.get_nodes("Analyst", {"name": owner_name})
        if not owner:
            print(f"Error: Owner '{owner_name}' not found. Please create the Lead Analyst first.")
            return

        self.create_node("Project", {"id": int(project_id), "name": project_name, "timeline": timeline, "description": description})
        self.create_relationship("Analyst", {"name": owner_name}, "Project", {"id": int(project_id)}, "OWNS")
        print(f"Project '{project_name}' created and assigned to {owner_name}.")

    def show_projects(self):
        query = """
            MATCH (u:Analyst)-[:OWNS]->(p:Project)
            RETURN p.name AS project, u.name AS owner, p.locked AS locked
        """
        projects = self.run_query(query, fetch=True)
        if projects:
            for project in projects:
                lock_status = "Locked" if project.get("locked") else "Unlocked"
                print(f"Project: {project['project']}, Owner: {project['owner']}, Status: {lock_status}")
        else:
            print("No projects found.")
