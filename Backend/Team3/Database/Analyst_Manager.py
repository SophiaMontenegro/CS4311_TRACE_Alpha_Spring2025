import logging

class AnalystManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_analyst(self, name, analyst_id, role="Analyst"):
        """
        Creates an analyst, can be assigned as Lead initially.
        """
        self.db_manager.create_node("User", {"id": analyst_id, "name": name, "role": role})

    def assign_lead(self, analyst_id):
        """
        Promotes an Analyst to a Lead Analyst.
        """

    def check_if_lead_and_member(self, analyst_name, project_name):
        role_check_query = """
        MATCH (a:Analyst)-[:PART_OF|OWNS]->(p:Project)
        WHERE a.name = $analyst_name AND p.name = $project_name
        RETURN a.role AS role, COUNT(p) > 0 AS in_project
        """

        result = self.db_manager.run_query(role_check_query, {"analyst_name": analyst_name, "project_name": project_name}, fetch=True)

        if not result:
            print(f"Error: Analyst '{analyst_name}' not found.")
            return False

        analyst_role = result[0]["role"]
        in_project = result[0]["in_project"]

        if analyst_role == 1  and in_project:
            return True
        else:
            return False


    def get_analyst_by_initials(self, initials):
        """Get an analyst by their initials"""
        try:
            result = self.db_manager.run_query(
                "MATCH (a:Analyst {name: $initials}) RETURN a",
                {"initials": initials},
                fetch=True
            )
            
            if result and len(result) > 0:
                return result[0]['a']
            return None
        except Exception as e:
            logging.error(f"Error getting analyst by initials: {e}")
            return None
        