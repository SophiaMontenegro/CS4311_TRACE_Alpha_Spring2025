from datetime import datetime
import uuid
import logging
class ProjectManager:
    def __init__(self, db_manager, analyst_manager):
        self.db_manager = db_manager
        self.analyst_manager = analyst_manager

    

    def create_project(self, analyst_id, project_name, start_date, end_date, description, userList):
        """
        Creates a new project with the given analyst as the owner.
        
        Parameters:
        - analyst_id: The ID of the analyst who will own the project
        - project_name: The name of the project
        - start_date: The start date of the project
        - end_date: The end date of the project
        - description: A description of the project
        - userList: A list of user initials to add as team members
        
        Returns:
        - The created project node or None if creation failed
        """
        try:
            logging.debug(f"Creating project: analyst_id={analyst_id}, name={project_name}")
            
            # Convert date objects to strings if they're not already
            start_date_str = start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
            end_date_str = end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
            
            # Generate a unique ID for the project
            project_id = str(uuid.uuid4())
            
            # Create project with the unique ID
            query = """
            MATCH (a:Analyst {id: $analyst_id})
            CREATE (p:Project {
                id: $project_id,
                name: $project_name,
                description: $description,
                start_date: $start_date,
                end_date: $end_date,
                locked: false,
                created_at: datetime()
            })
            CREATE (a)-[:OWNS]->(p)
            RETURN p
            """
            
            params = {
                "analyst_id": analyst_id,
                "project_id": project_id,
                "project_name": project_name,
                "description": description,
                "start_date": start_date_str,
                "end_date": end_date_str
            }
            
            logging.debug(f"Running query with params: {params}")
            result = self.db_manager.run_query(query, params, fetch=True)
            
            logging.debug(f"Project creation query result: {result}")
            
            if not result or len(result) == 0:
                logging.error("No result returned from project creation query")
                return None
            
            # Project was created successfully
            logging.debug(f"Created project with ID: {project_id}")
            
            # Add team members if provided
            if userList and len(userList) > 0:
                for user_initials in userList:
                    logging.debug(f"Adding team member: {user_initials}")
                    # Find the analyst by initials
                    analyst = self.analyst_manager.get_analyst_by_initials(user_initials)
                    logging.debug(f"Found analyst for {user_initials}: {analyst}")
                    
                    if analyst:
                        try:
                            # Create relationship between analyst and project
                            team_query = """
                            MATCH (a:Analyst {id: $analyst_id})
                            MATCH (p:Project {id: $project_id})
                            CREATE (a)-[:PART_OF]->(p)
                            """
                            team_params = {
                                "analyst_id": analyst["id"],
                                "project_id": project_id
                            }
                            logging.debug(f"Running team member query with params: {team_params}")
                            
                            team_result = self.db_manager.run_query(team_query, team_params)
                            logging.debug(f"Team member addition result: {team_result}")
                            
                            logging.debug(f"Added team member {user_initials} with ID {analyst['id']} to project {project_id}")
                        except Exception as e:
                            logging.error(f"Error adding team member {user_initials}: {e}", exc_info=True)
                    else:
                        logging.warning(f"Team member not found: {user_initials}")
            
            return result[0]['p']
        except Exception as e:
            logging.error(f"Error in create_project: {e}", exc_info=True)
            return None

    # def create_project(self, owner_name, project_name, startDate, endDate, description, userList):
    #     """
    #     Creates a new project and assigns a PART_OF relationship for each user in userList.
    #     """
    
    #     # Generate unique project ID and timestamp
    #     timestamp = datetime.utcnow().isoformat()
    #     project_id = str(uuid.uuid4())
    
    #     # Check if the owner exists
    #     owner_query = """
    #         MATCH (u:Analyst {name: $owner_name})
    #         RETURN u
    #     """
    #     owner = self.db_manager.run_query(owner_query, {"owner_name": owner_name}, fetch=True)
    
    #     if not owner:
    #         print(f"Error: Owner '{owner_name}' not found. Please create the Lead Analyst first.")
    #         return None

    #     # To check if the project with the same name is already created(existing)
    #     existingProject = self.db_manager.run_query(
    #         "MATCH (p:Project {name:$name}) RETURN p",
    #         {"name":project_name}
    #     )
        
    #     if existingProject:
    #         print(f"The project with the name: {project_name} already exist")
    #         return False
        
    #     # Create the project node
    #     project_query = """
    #         CREATE (p:Project {name: $project_name, id: $project_id, startDate: $startDate, 
    #                 endDate: $endDate, description: $description, locked: false, timestamp: $timestamp})
    #         RETURN p
    #     """
    #     self.db_manager.run_query(project_query, {
    #         "project_name": project_name,
    #         "project_id": project_id,
    #         "startDate": startDate,
    #         "endDate": endDate,
    #         "description": description,
    #         "timestamp": timestamp
    #     })
    
    #     # Create ownership relationship
    #     ownership_query = """
    #         MATCH (u:Analyst {name: $owner_name}), (p:Project {id: $project_id})
    #         MERGE (u)-[:OWNS]->(p)
    #     """
    #     self.db_manager.run_query(ownership_query, {"owner_name": owner_name, "project_id": project_id})
    
    #     # Create PART_OF relationships for each user in userList
    #     for user in userList:
    #         user_query = """
    #             MATCH (a:Analyst {name: $user_name})
    #             RETURN a
    #         """
    #         user_exists = self.db_manager.run_query(user_query, {"user_name": user}, fetch=True)
    
    #         if not user_exists:
    #             print(f"User '{user}' not found. Creating new Analyst node.")
    #             create_user_query = "CREATE (a:Analyst {name: $user_name})"
    #             self.db_manager.run_query(create_user_query, {"user_name": user})
    
    #         # Create relationship
    #         part_of_query = """
    #             MATCH (a:Analyst {name: $user_name}), (p:Project {id: $project_id})
    #             MERGE (a)-[:PART_OF]->(p)
    #         """
    #         self.db_manager.run_query(part_of_query, {"user_name": user, "project_id": project_id})
    
    #     print(f"✅ Project '{project_name}' created successfully and users have been assigned.")
    #     return True

    def show_projects(self):
        """
        Displays all projects with their owners and lock status.
        """
        query = """
            MATCH (u:Analyst)-[:OWNS]->(p:Project)
            RETURN p.name AS project, u.name AS owner, p.locked AS locked
        """
        projects = self.db_manager.run_query(query, fetch=True)
        if projects:
            for project in projects:
                lock_status = "Locked" if project["locked"] else "Unlocked"
                print(f"Project: {project['project']}, Owner: {project['owner']}, Status: {lock_status}")
        else:
            print("No projects found.")

    def _get_project_lock_status(self, project_name):
        """
        Retrieves the current lock status of the project.
        """
        query = """
        MATCH (p:Project {name: $project_name})
        RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(query, {"project_name": project_name}, fetch=True)
        return result[0]["locked"] if result else None

    def lock_project(self, project_name, analyst_name):
        """
        Locks a project (only the Lead of that project can do this).
        """
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project_name):
            print(f"Error: Analyst '{analyst_name}' is not the lead of project '{project_name}' and cannot lock it.")
            return

        lock_query = """
        MATCH (p:Project {name: $project_name})
        WHERE NOT p.locked
        SET p.locked = true
        RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(lock_query, {"project_name": project_name}, fetch=True)

        if result and result[0]["locked"]:
            print(f"Project '{project_name}' is now locked.")
        else:
            print(f"Error: Failed to lock project '{project_name}'. It might already be locked.")

    def unlock_project(self, project_name, analyst_name):
        """
        Unlocks a project (only the Lead of that project can do this).
        """
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project_name):
            print(f"Error: Analyst '{analyst_name}' is not the lead of project '{project_name}' and cannot unlock it.")
            return

        unlock_query = """
        MATCH (p:Project {name: $project_name})
        WHERE p.locked
        SET p.locked = false
        RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(unlock_query, {"project_name": project_name}, fetch=True)

        if result and not result[0]["locked"]:
            print(f"Project '{project_name}' is now unlocked.")
        else:
            print(f"Error: Failed to unlock project '{project_name}'. It might already be unlocked.")

    def toggle_project_lock(self, project_name, analyst_name):
        """
        Toggles the lock status of a project (only the Lead of that project can do this).
        Calls `lock_project` or `unlock_project` based on the current status.
        """
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project_name):
            print(f"Error: Analyst '{analyst_name}' is not the lead of project '{project_name}' and cannot toggle the lock status.")
            return None

        current_status = self._get_project_lock_status(project_name)
        if current_status is None:
            print(f"Error: Project '{project_name}' not found.")
            return None

        if current_status:
            self.unlock_project(project_name, analyst_name)
            return False
        else:
            self.lock_project(project_name, analyst_name)
            return True

    def delete_project(self, analyst, project_name):
        """
        Deletes a project only if the analyst is a Lead Analyst and the project is not locked.
        """

        # Verify if the analyst is a Lead Analyst
        if not self.analyst_manager.check_if_lead_and_member(analyst, project_name):
            print(f"Error: Analyst '{analyst}' does not have permission to delete project '{project_name}'. Only a Lead Analyst can delete a project.")
            return None

        # Check if the project exists and retrieve its lock status
        query_check_lock = """
            MATCH (p:Project {name: $project_name})
            RETURN p.name AS name, p.locked AS locked
        """
        params = {"project_name": project_name}
        result = self.db_manager.run_query(query_check_lock, params, fetch=True)

        print(f"Query result for project '{project_name}': {result}")  # Debugging line

        if not result:  # If the query returns no results, the project doesn't exist
            print(f"Error: Project '{project_name}' not found.")
            return None

        project_data = result[0]
        print(f"Found project: {project_data}")  # Debugging line

        if project_data["locked"]:  # If the project is locked, prevent deletion
            print(f"Error: Project '{project_name}' is locked and cannot be deleted.")
            return None

        # Proceed with project deletion
        query_delete = """
            MATCH (p:Project {name: $project_name})
            DETACH DELETE p
        """
        self.db_manager.run_query(query_delete, params)

        print(f"Project '{project_name}' has been deleted successfully by {analyst}.")
        return True


    def save_project(self, project_id):
        """
        Saves changes to a project.
        (Implementation idea: save a snapshot of project details)
        """
        """
        Saves a project by updating its status to 'Saved' and setting a last_updated timestamp.
        """
        query = """
        MATCH (p:Project {project_id: $project_id})
        SET p.status = $status, p.last_updated = $timestamp
        RETURN p.project_id, p.name, p.status, p.last_updated
        """
        timestamp = datetime.utcnow().isoformat()
        return self.db_managerdb.query(query, {"project_id": project_id, "status": status, "timestamp": timestamp})

    def load_project(self, project_id, analyst):
        """
        Loads and retrieves a project's details by its project_id.
        Ensures that the project exists before returning its details.
        """
        query = """
            MATCH (p:Project {id: $project_id})
            OPTIONAL MATCH (a:Analyst)-[:OWNS]->(p)
            RETURN p.id AS id, p.name AS project_name, p.description AS description, 
                p.status AS status, p.startDate AS startDate, p.endDate AS endDate, p.locked AS locked, 
                a.name AS lead_analyst
        """
        result = self.db_manager.run_query(query, {"project_id": project_id}, fetch=True)

        if result:
            project = result[0]
            return {
                "id": project.get("id"),
                "name": project.get("project_name"),
                "description": project.get("description"),
                "status": project.get("status"),
                "startDate": project.get("startDate"),
                "endDate": project.get("endDate"),
                "locked": project.get("locked"),
                "lead_analyst": project.get("lead_analyst"),
            }
        else:
            print(f"Error: Project '{project_id}' not found.")
            return None


    def change_lead(self, new_lead, project_name, lead_changer):
    # lead_changer is the analyst making this change
    # Check if the new lead exists and is a Lead Analyst
        query = """
        MATCH (a:Analyst)
        WHERE a.name = $new_lead AND a.role = $role
        RETURN COUNT(a) > 0 AS has_role
        """
        result = self.db_manager.run_query(query, {"new_lead": new_lead, "role": 1}, fetch=True)
        if not result or not result[0]["has_role"]:
            print(f"Error: '{new_lead}' is not a Lead Analyst or does not exist.")
            return
        project_query = """
        MATCH (p:Project)
        WHERE p.name = $project_name
        RETURN p.id AS project_id
        """
        project_result = self.db_manager.run_query(project_query, {"project_name": project_name}, fetch=True)
        if not project_result:
            print(f"Error: Project '{project_name}' not found.")
            return
        project_id = project_result[0]["project_id"]  # project_id is a string (UUID)
        owner_query = """
        MATCH (a:Analyst)-[:OWNS]->(p:Project)
        WHERE p.id = $project_id
        RETURN a.name AS owner_name
        """
        owner_result = self.db_manager.run_query(owner_query, {"project_id": project_id}, fetch=True)
        if not owner_result or owner_result[0]["owner_name"] != lead_changer:
            print(f"Error: '{lead_changer}' is not the current owner of the project '{project_name}' and cannot change the lead.")
            return
        delete_query = """
        MATCH (a:Analyst)-[r:OWNS]->(p:Project)
        WHERE p.id = $project_id
        DELETE r
        """
        self.db_manager.run_query(delete_query, {"project_id": project_id})
        add_participant_query = """
        MATCH (a:Analyst), (p:Project)
        WHERE a.name = $owner_name AND p.id = $project_id
        MERGE (a)-[:PART_OF]->(p)
        """
        self.db_manager.run_query(add_participant_query, {"owner_name": owner_result[0]["owner_name"], "project_id": project_id})
        self.db_manager.create_relationship("Analyst", {"name": new_lead}, "Project", {"id": project_id}, "OWNS")
        print(f"Project '{project_name}' is now owned by {new_lead}.")
        self.db_manager.create_relationship("Analyst", {"name": new_lead}, "Project", {"id": project_id}, "PART_OF")
        print(f"New lead '{new_lead}' added as a participant in the project.")



    def edit_project_members(self, project_name, action, participant_name, analyst_name):
        # Check if the analyst has the correct role (Lead or member) for the project
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project_name):
            print(f"Error: Analyst '{analyst_name}' isn't part of the current project or doesn't have permission.")
            return
    
        project_exists_query = """
        MATCH (p:Project {name: $project_name})
        RETURN p.id AS project_id, COUNT(p) > 0 AS project_exists
        """
        result = self.db_manager.run_query(project_exists_query, {"project_name": project_name}, fetch=True)
        
        if not result or not result[0]["project_exists"]:
            print(f"Error: Project '{project_name}' not found.")
            return
        
        project_id = result[0]["project_id"]
    
        if action == "add":
            existing_person = self.db_manager.get_nodes("Analyst", {"name": participant_name})
    
            if not existing_person:
                print(f"User '{participant_name}' not found. Creating a new Analyst node.")
                self.db_manager.create_node("Analyst", {"name": participant_name})

            already_part_of_project_query = """
            MATCH (a:Analyst)-[:PART_OF]->(p:Project)
            WHERE a.name = $participant_name AND p.id = $project_id
            RETURN COUNT(a) > 0 AS is_part_of_project
            """
            existing_relation = self.db_manager.run_query(already_part_of_project_query, 
                                               {"participant_name": participant_name, "project_id": project_id}, fetch=True)
    
            if existing_relation and existing_relation[0]["is_part_of_project"]:
                print(f"User '{participant_name}' is already part of the project '{project_name}'. No action taken.")
                return

            self.db_manager.create_relationship("Analyst", {"name": participant_name}, "Project", {"id": project_id}, "PART_OF")
            print(f"User '{participant_name}' added to project '{project_name}'.")
    
        elif action == "remove":

            check_participant_query = """
            MATCH (a:Analyst)-[r:PART_OF]->(p:Project)
            WHERE a.name = $participant_name AND p.id = $project_id
            RETURN COUNT(r) > 0 AS is_part_of_project
            """
            existing_relation = self.db_manager.run_query(check_participant_query, 
                                               {"participant_name": participant_name, "project_id": project_id}, fetch=True)
    
            if not existing_relation or not existing_relation[0]["is_part_of_project"]:
                print(f"Error: User '{participant_name}' is not part of the project '{project_name}'.")
                return

            delete_query = """
            MATCH (a:Analyst {name: $participant_name})-[r:PART_OF]->(p:Project {id: $project_id})
            DELETE r
            """
            self.db_manager.run_query(delete_query, {"participant_name": participant_name, "project_id": project_id})
            print(f"User '{participant_name}' removed from project '{project_name}'.")
    
        else:
            print("Invalid action. Use 'add' or 'remove'.")


    def change_project_name(self, current_name, new_name, analyst_name):
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, current_name):
            print(f"Error: Analyst '{analyst_name}' isn't part of the current project or doesn't have permission.")
        
        check_query = """
        MATCH (p:Project)
        WHERE p.name = $current_name
        RETURN COUNT(p) > 0 AS project_exists
        """
        result = self.db_manager.run_query(check_query, {"current_name": current_name}, fetch=True)

        if not result or not result[0]["project_exists"]:
            print(f"Error: Project '{current_name}' not found.")
            return

        update_query = """
        MATCH (p:Project)
        WHERE p.name = $current_name
        SET p.name = $new_name
        """
        self.db_manager.run_query(update_query, {"current_name": current_name, "new_name": new_name})

        print(f"Project name changed from '{current_name}' to '{new_name}'.")


    def edit_timeline(self, project, analyst_name, end_date):
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project):
            print(f"Error: Analyst '{analyst_name}' isn't part of the current project or doesn't have permission.")
        
        check_query = """
        MATCH (p:Project)
        WHERE p.name = $project
        RETURN COUNT(p) > 0 AS project_exists
        """
        result = self.db_manager.run_query(check_query, {"project": project}, fetch=True)
        if not result or not result[0]["project_exists"]:
            print(f"Error: Project '{project}' not found.")
            return
        update_query = """
        MATCH (p:Project)
        WHERE p.name = $project
        SET p.end = $end_date
        """
        self.db_manager.run_query(update_query, {"project": project, "end_date": end_date})
        print(f"Successfully updated end date of '{project}' to {end_date}.")

