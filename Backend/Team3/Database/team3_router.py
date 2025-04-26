from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from datetime import datetime
import pytz
import logging
from Team3.Database.Project_Manager import ProjectManager
from Team3.Database.Database_Manager import Database_Manager
from Team3.Database.Analyst_Manager import AnalystManager
from Team3.Database.File_Manager import FileManager

# ✅ Initialize DB connection and project manager
try:
    db = Database_Manager()  # No arguments needed anymore
    analyst_manager = AnalystManager(db)
    project_manager = ProjectManager(db, analyst_manager)
    file_manager = FileManager()
    print("✅ Database connection successful for Team 3")
except Exception as e:
    print(f"Team 3 database connection failed ❌: {e}")

# Create router
team3_router = APIRouter(prefix="/team3", tags=["team3"])

# Pydantic model for project creation
class ProjectCreate(BaseModel):
    analyst_id: str
    project_name: str
    start_date: date
    end_date: date
    description: str
    userList: list
    port: int
    directory_path: str

# ✅ Create a project
@team3_router.post("/projects/")
async def create_project(project: ProjectCreate):
    try:
        # Add logging to debug
        logging.debug(f"Received project creation request: {project}")
        
        project_data = project.model_dump()
        logging.debug(f"Project data after model_dump: {project_data}")
        
        success = project_manager.create_project(
            project_data['analyst_id'],
            project_data['project_name'],
            project_data['start_date'],
            project_data['end_date'],
            project_data['description'],
            project_data['userList'],
            project_data['port'],
            project_data['directory_path']
        )
        
        logging.debug(f"Project creation result: {success}")
        """
        if success is False:
            logging.error("A project with this name already exists.")
            raise HTTPException(status_code=409, detail="A project with this name already exists.")
        """
        if success is None:
            logging.error("Project creation failed")
            raise HTTPException(status_code=500, detail="Project creation failed")

        return {"message": "Project created successfully", "project": project_data}
    except Exception as e:
        logging.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ProjectNameCheckRequest(BaseModel):
    project_name: str
    analyst_initials: str

@team3_router.post("/project_name/")
async def verify_project_name(data: ProjectNameCheckRequest):
    try:
        logging.debug(f"Received project creation request: {data.project_name}")
        success = project_manager.verify_project_name(data.project_name, data.analyst_initials)
        print("LOOOOOOK: ", success)
        if not success:
            return {"status": "taken"}
        return {"status": "available"}
    except Exception as e:
        logging.error(f"Error in verifying project name: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Lock/Unlock a project
@team3_router.put("/projects/{project_name}/lock")
async def lock_project(project_name: str, analyst_id: str):
    print(f"Toggling lock for project {project_name} by analyst {analyst_id}")
    success = project_manager.toggle_project_lock(project_name, analyst_id)
    if success is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project lock state changed successfully", "locked": success}

# ✅ Delete a project (only if unlocked) -> Move to deleted projects database
@team3_router.delete("/projects/{project_name}/delete")
async def delete_project(project_name: str, analyst_id: str):
    print(f"Delete {project_name} by analyst {analyst_id}")
    success = project_manager.delete_project(analyst_id, project_name)
    if success is None:
        raise HTTPException(status_code=403, detail="Project is locked or does not exist")
    return {"message": "Project deleted successfully"}

# ✅ Restore a project
@team3_router.put("/projects/{project_name}/restore")
async def restore_project(project_name: str, analyst_initials: str):
    print(f"Restoring {project_name} by analyst {analyst_initials}")
    success = project_manager.restore_project(project_name, analyst_initials)
    if success is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project restored successfully"}

# ✅ Permanently delete  a project
@team3_router.put("/projects/{project_name}/permanently_delete")
async def fully_delete_project(project_name: str, analyst_initials: str):
    print(f"Permanently deleting {project_name} by analyst {analyst_initials}")
    success = project_manager.fully_delete_project(project_name, analyst_initials)
    if success is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project permanently deleted successfully"}

# Analyst verification model
class AnalystVerify(BaseModel):
    initials: str

# Verify analyst endpoint
@team3_router.post("/analysts/verify")
async def verify_analyst(analyst: AnalystVerify):
    try:
        # Query the database to check if the analyst exists
        analyst_exists = project_manager.db_manager.run_query(
            "MATCH (a:Analyst {name: $initials}) RETURN a",
            {"initials": analyst.initials},
            fetch=True
        )
        
        if analyst_exists and len(analyst_exists) > 0:
            # Return the analyst ID if found
            return {
                "message": "Analyst verified successfully",
                "analyst_id": analyst_exists[0]['a']['id']
            }
        else:
            raise HTTPException(status_code=404, detail="Analyst not found")
    except Exception as e:
        logging.error(f"Error verifying analyst: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyst registration model
class AnalystRegister(BaseModel):
    initials: str
    name: str

# Register analyst endpoint
@team3_router.post("/analysts/register")
async def register_analyst(analyst: AnalystRegister):
    try:
        # Check if analyst with these initials already exists
        existing_analyst = project_manager.db_manager.run_query(
            "MATCH (a:Analyst {name: $initials}) RETURN a",
            {"initials": analyst.initials},
            fetch=True
        )
        
        if existing_analyst and len(existing_analyst) > 0:
            raise HTTPException(status_code=409, detail="Analyst with these initials already exists")
        
        # Create new analyst with the required format
        result = project_manager.db_manager.run_query(
            "CREATE (a:Analyst {id: randomUUID(), name: $initials, role: 1}) RETURN a",
            {"initials": analyst.initials},
            fetch=True
        )
        
        if result and len(result) > 0:
            return {
                "message": "Analyst registered successfully",
                "analyst_id": result[0]['a']['id']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to register analyst")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error registering analyst: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def format_date(dt_obj):
    try:
        if dt_obj is None:
            return ""  # or "N/A" or None

        # If it's a Neo4j datetime object, convert to ISO string first
        if hasattr(dt_obj, "to_native"):  # neo4j.time.DateTime
            dt_obj = dt_obj.to_native()

        # If it's a string, make sure it's parsed correctly
        if isinstance(dt_obj, str):
            dt_obj = datetime.fromisoformat(dt_obj.replace("Z", "+00:00"))

        # Convert to local timezone (e.g., Eastern Time)
        local_tz = pytz.timezone("America/New_York")
        local_time = dt_obj.astimezone(local_tz)

        # Return formatted string
        return local_time.strftime("%m-%d-%y %H:%M")

    except Exception as e:
        logging.error(f"Error formatting date: {e}")
        return ""

# Get projects by analyst ID
@team3_router.get("/projects/analyst/{analyst_id}")
async def get_analyst_projects(analyst_id: str):
    try:
        # Query projects owned by this analyst
        projects = project_manager.db_manager.run_query(
            """
            MATCH (a:Analyst {id: $analyst_id})-[:OWNS]->(p:Project)
            RETURN p
            ORDER BY p.created_at DESC
            """,
            {"analyst_id": analyst_id},
            fetch=True
        )
        
        if projects is None:
            projects = []
            
        # Format the projects for the frontend
        formatted_projects = []
        for project_record in projects:
            project = project_record['p']
            formatted_projects.append({
                "id": project.get("id"),
                "name": project.get("name"),
                "lead_analyst": project.get("lead_analyst", ""),
                "description": project.get("description", ""),
                "start_date": format_date(project.get("start_date")),
                "end_date": format_date(project.get("end_date")),
                "locked": project.get("locked", False),
                "created_at": format_date(project.get("created_at")),
                "last_edited": format_date(project.get("last_edited")),
                "port": project.get("port", 0),
                "directory_path": project.get("directory_path", "")
            })
            
        return {"projects": formatted_projects}
    except Exception as e:
        logging.error(f"Error fetching analyst projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get projects by analyst ID
@team3_router.get("/projects_shared/analyst/{analyst_id}")
async def get_analyst_shared_projects(analyst_id: str):
    try:
        # Query projects owned by this analyst
        # projects = project_manager.show_Part_Of_projects(analyst_id)
        projects = project_manager.db_manager.run_query(
            """
            MATCH (a:Analyst {name: $analyst_id})-[:PART_OF]->(p:Project)
            RETURN p
            ORDER BY p.created_at DESC
            """,
            {"analyst_id": analyst_id},
            fetch=True
        )

        if projects is None:
            projects = []

        # Format the projects for the frontend
        formatted_projects = []
        for project_record in projects:
            project = project_record['p']
            formatted_projects.append({
                "id": project.get("id"),
                "name": project.get("name"),
                "lead_analyst": project.get("lead_analyst", ""),
                "description": project.get("description", ""),
                "start_date": format_date(project.get("start_date")),
                "end_date": format_date(project.get("end_date")),
                "locked": project.get("locked", False),
                "created_at": format_date(project.get("created_at")),
                "last_edited": format_date(project.get("last_edited")),
                "port": project.get("port", 0),
                "directory_path": project.get("directory_path", "")
            })

        return {"projects": formatted_projects}
    except Exception as e:
        logging.error(f"Error fetching analyst projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get deleted projects by analyst ID
@team3_router.get("/projects_deleted/analyst/{analyst_id}")
async def get_deleted_projects(analyst_id: str):
    try:
        # Query projects owned by this analyst
        projects = project_manager.db_manager.run_query(
            """
            MATCH (a:Analyst {id: $analyst_id})-[:OWNS]->(p:Deleted)
            RETURN p
            ORDER BY p.created_at DESC
            """,
            {"analyst_id": analyst_id},
            fetch=True
        )

        if projects is None:
            projects = []

        # Format the projects for the frontend
        formatted_projects = []
        for project_record in projects:
            project = project_record['p']
            formatted_projects.append({
                "id": project.get("id"),
                "name": project.get("name"),
                "lead_analyst": project.get("lead_analyst", ""),
                "description": project.get("description", ""),
                "start_date": format_date(project.get("start_date")),
                "end_date": format_date(project.get("end_date")),
                "locked": project.get("locked", False),
                "created_at": format_date(project.get("created_at")),
                "last_edited": format_date(project.get("last_edited")),
                "port": project.get("port", 0),
                "directory_path": project.get("directory_path", "")
            })

        return {"projects": formatted_projects}
    except Exception as e:
        logging.error(f"Error fetching analyst projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get all users in a project
@team3_router.get("/projects/get_analyst/{project_name}")
async def get_analysts(project_name: str):
    try:
        # Query analysts part of a project
        analysts = project_manager.db_manager.run_query(
            """
            MATCH (a:Analyst)-[:PART_OF]->(p:Project {name: $project_name})
            RETURN a.name""",
            {"project_name": project_name},
            fetch=True
        )

        # Extract just the names
        analysts = [record["a.name"] for record in analysts] if analysts else []

        return {"analysts": analysts}
    except Exception as e:
        logging.error(f"Error fetching analysts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@team3_router.put("/projects/{project_name}/member_added")
async def add_project_member(project_name: str, new_user: str, lead_analyst: str):
    success = project_manager.edit_project_members(project_name, "add", new_user, lead_analyst)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": "Analyst added successfully"}

@team3_router.put("/projects/{project_name}/member_removed")
async def remove_project_member(project_name: str, new_user: str, lead_analyst: str):
    success = project_manager.edit_project_members(project_name, "remove", new_user, lead_analyst)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": "Analyst removed successfully"}

# Change project name
@team3_router.put("/projects/{project_name}/name")
async def change_project_name(project_name: str, new_name: str, analyst_name: str):
    success = project_manager.change_project_name(project_name, new_name, analyst_name)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": f"Project name changed to {new_name} successfully"}

# Edit end date/timeline
@team3_router.put("/projects/{project_name}/timeline")
async def edit_timeline(project_name: str, end_date: date, analyst_name: str):
    success = project_manager.edit_timeline(project_name, analyst_name, end_date)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": f"Project end date updated successfully to {end_date}"}

# Edit description
@team3_router.put("/projects/{project_name}/description")
async def edit_description(project_name: str, description: str, analyst_name: str):
    success = project_manager.edit_description(project_name, analyst_name, description)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": f"Project description updated successfully to {description}"}

# Edit last edited
@team3_router.put("/projects/{project_name}/last_edited")
async def edit_last_edited(project_name: str):
    success = project_manager.edit_last_edited(project_name)
    if success is None:
        raise HTTPException(status_code=404, detail="Project doesn't exist")
    return {"message": f"Project updated last_edited sucessfully"}

# Edit port
@team3_router.put("/projects/{project_name}/port")
async def edit_port(project_name: str, port: int, analyst_name: str):
    success = project_manager.edit_port(project_name, analyst_name, port)
    if success is None:
        raise HTTPException(status_code=404, detail="Analyst doesn't exist")
    return {"message": f"Project port updated successfully to {port}"}

class PathVerifyRequest(BaseModel):
    directory_path: str

# Directory Path Verification
@team3_router.put("/directory_path_verify/")
async def verify_directory_path(data: PathVerifyRequest):
    success = file_manager.is_valid_path(data.directory_path)
    if not success:
        return {"status": "invalid"}
    return {"status": "available"}

# Create Directories
@team3_router.put("/directories/{project_name}/create")
async def create_directories(directory_path: str, project_name: str):
    success = file_manager.fileCreation(directory_path, project_name)
    if success is None:
        raise HTTPException(status_code=404, detail="Directory Path doesn't exist")
    return {"message": f"Directories created at {directory_path} "}