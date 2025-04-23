from Database_Manager import DatabaseManager

class AnalystManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_analyst(self, name, analyst_id, role="Analyst"):
        """
        Creates an analyst, can be assigned as Lead initially.
        """
        # Checks is the analyst name or the initials is already in use
        existingAnalyst = self.db_manager.run_query(
            "MATCH (u:User) WHERE u.name STARTS WITH $name RETURN u.name",
            {"name":name}
        )
        # Add number after initial
        if existingAnalyst:
            count = 1
            newInitial = name
            existingAnalyst = [record["u.name"] for record in existingAnalyst]
            while newInitial in existingAnalyst:
                newInitial = f"{name}{count}"
                count +=1
            name = newInitial

        self.db_manager.create_node("User", {"id": analyst_id, "name": name, "role": role})
        print(f"Analyst {name} has been created.")
        return True

    def assign_lead(self, analyst_id):
        """
        Promotes an Analyst to a Lead Analyst.
        """
        query = """
        MATCH (u:User {id: $analyst_id})
        SET u.role = 'Lead'
        RETURN u
        """
        result = self.db_manager.run_query(query,{"analyst_id": analyst_id})
        return result.single() is not None

    def is_Lead(self, analyst_id):
        """
        Checks if an analyst is a Lead
        """
        query = """
        MATCH (u:User {id: $analyst_id})
        RETURN u.role AS role
        """
        result = self.db_manager.run_query(query,{"analyst_id": analyst_id})
        return result.single() is not None and result["role"]=="Lead"
    
    # Test cases for Analyst
if __name__ == "__main__":

    dbm = DatabaseManager()
    am = AnalystManager(db) 

    """--- Test to create analyst"""
    print("\n Test Case: creating an Analyst")
    am.create_analyst("Gabe","Gp1")

    print("\n Test Case: creating an Analyst")
    am.create_analyst("Gabe","Gp2")

    """--- To assign to a lead role"""
    print("Assign analyst if lead")
    am.assign_lead("Gp2")

    """--- Test case to check if is lead"""
    print("Check if analyst is lead", am.is_Lead("Gp2"))