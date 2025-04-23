from Database_Manager import  Database_Manager
from datetime import datetime
import os
import json

class ProjectManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_project(self, project_name, project_id, owner_name, start_date, end_date, description):
        """
        Only a Lead Analyst can create a project.
        """
        # Check if the owner is a Lead and queries to create a new project with start and end dates
        lead_check = self.db_manager.run_query(
            "MATCH (u:User {name:$name}) RETURN u.role",
            {"name":owner_name}
        )

        # If the role is not a lead will display this message
        if not lead_check or lead_check[0]['u.role'] != 'lead':
            print("Only the Lead Analyst can create a project!")
        
        # Variable to get the current time
        currentTime = datetime.now().isoformat()

        # To check if the project with the same name is already created(existing)
        existingProject = self.db_manager.run_query(
            "MATCH (p:Project {name:$name}) RETURN p",
            {"name":project_name}
        )
        
        if existingProject:
            print(f"The project with the name: {project_name} already exist")
            return False


        #creates a project in neo4j
        self.db_manager.run_query(
            """
            CREATE (p:Project {
            name: $name, 
            id: $id, 
            owner: $owner_name,
            start_date: $start_date,
            end_date: $end_date, 
            description: $description,
            timestamp: $timestamp})
            """,
            {
            "name":project_name,
            "id":project_id,
            "owner":owner_name,
            "start_time":start_date,
            "end_time":end_date,
            "description":description,
            "timestamp": currentTime,

            }
        )
        self.db_manager.run_query(
            """
            """
        )
        print(f"Project {project_name} was created successfully.")
        return True

    def show_projects(self):
        """
        Fetches and displays all projects.
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


    def lock_project(self, user, project):
        """
        Locks a project if the user owns it.
        """
        query = """
            MATCH (u:Analyst {name: $user})-[:OWNS]->(p:Project {name: $project})
            WHERE NOT p.locked
            SET p.locked = true
            RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(query, {"user": user, "project": project}, fetch=True)
        if result and result[0]["locked"]:
            print(f"Project '{project}' is now locked.")
        else:
            print(f"Error: User '{user}' does not own project '{project}' or it is already locked.")



    def unlock_project(self, user, project):
        """
        Unlocks a project.
        """
        query = """
            MATCH (u:Analyst {name: $user})-[:OWNS]->(p:Project {name: $project})
            WHERE p.locked
            SET p.locked = false
            RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(query, {"user": user, "project": project}, fetch=True)
        if result and not result[0]["locked"]:
            print(f"Project '{project}' is now unlocked.")
        else:
            print(f"Error: User '{user}' does not own project '{project}' or it is already unlocked.")

    def toggle_project_lock(self, project_name, analyst_name):
        """
        Toggles the lock status of a project (only the Lead of that project can do this).
        Calls `lock_project` or `unlock_project` based on the current status.
        """
        if not self.analyst_manager.check_if_lead_and_member(analyst_name, project_name):
            print(f"Error: Analyst '{analyst_name}' is not the lead of project '{project_name}' and cannot toggle the lock status.")
            return

        current_status = self._get_project_lock_status(project_name)
        if current_status is None:
            print(f"Error: Project '{project_name}' not found.")
            return

        if current_status:
            self.unlock_project(project_name, analyst_name)
        else:
            self.lock_project(project_name, analyst_name)

    def delete_project(self, analyst, project_id):
        """
        Deletes a project only if the analyst is a Lead Analyst and the project is not locked.
        """
        # Verify if the analyst is a Lead Analyst
        if not self.is_LeadAnalyst(project_id, analyst):
            print(f"Error: Analyst '{analyst}' does not have permission to delete project '{project_id}'. Only a Lead Analyst can delete a project.")
            return None

        # Check if the project is locked
        query_check_lock = """
            MATCH (p:Project {id: $project_id})
            RETURN p.locked AS locked
        """
        result = self.db_manager.run_query(query_check_lock, {"project_id": project_id}, fetch=True)
        if result and result[0]["locked"]:
            print(f"Error: Project '{project_id}' is locked and cannot be deleted.")
            return None

        # Proceed with project deletion
        query_delete = """
            MATCH (p:Project {id: $project_id})
            DETACH DELETE p
        """
        self.db_manager.run_query(query_delete, {"project_id": project_id})
        
        print(f"Project '{project_id}' has been deleted successfully by {analyst}.")

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
        
    def edit_project(self, project_id, updates):
        """
        Edits project details (e.g., rename, add/remove analysts, edit timeline, change ownership).
        """

        # pay require helper functions


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

    # Methods to import and export projects
    def export_project(self,project_id, output_dir = "exports"):
        query = """
          MATCH (p:Project {id: $project_id})
          OPTIONAL MATCH (a:Analyst) - [:OWNS|PART_OF]->(p)
          RETURN p, collect(DISTINCT a.name) AS analysts 
        """
        result = self.db_manager.run_query(query, {"project_id":project_id}, fetch = True)
        if not result:
            print("No project found to export")
            return
        
        prjData = result[0]["p"] #Project data
        analysts = result[0]["analysts"]
        prjData["analysts"] = analysts

        os.makedirs(output_dir,exist_ok=True)
        filepath = os.path.join(output_dir,f"{prjData['name'].replace(' ','_')}_{project_id}.json")
        with open(filepath,"w") as f:
            json.dump(prjData, f, indent=1)
        
        print(f"Project {prjData['name']} exported successfully.")
    
    def import_project(self,json_file):

        if not os.path.exists(json_file):
            print(f"Error: File {json_file} not found.")
            return

        with open(json_file,"r") as file:
            prjData = json.load(file)

        check = self.db_manager.run_query(
            "MATCH (p:Project {id: $id}) RETURN p", {"id": prjData["id"]}
        )        

        if check:
            print(f"ERROR: Project {prjData['name']} already found.")
        
        self.db_manager.create_node("Project",[])

        for i in prjData.get("analysts",[]):
            self.db_manager.create_relationship("Analyst", {"name": i}, "Project", {"id": prjData["id"]}, "PART_OF")

        print(f"Project '{prjData['i']}' has been imported.")