import logging

class AnalystManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_analyst(self, name, analyst_id, role="Analyst"):
        """
        Creates an analyst, can be assigned as Lead initially.
        """
        self.db_manager.create_node("User", {"id": analyst_id, "name": name, "role": role})


    def check_if_lead(self, analyst_name, project_name):
        query = """
        MATCH (a:Analyst)-[:OWNS]->(p:Project)
        WHERE a.name = $analyst_name AND p.name = $project_name
        RETURN COUNT(*) > 0 AS is_owner
        """

        result = self.db_manager.run_query(
            query,
            {"analyst_name": analyst_name, "project_name": project_name},
            fetch=True
        )

        return result[0]["is_owner"] if result else False


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
        