from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
import logging
from Team3.Database.Project_Manager import ProjectManager
from Team3.Database.Database_Manager import Database_Manager
from Team3.Database.Analyst_Manager import AnalystManager

# ✅ Initialize DB connection and project manager
try:
    db = Database_Manager()  # No arguments needed anymore
    analyst_manager = AnalystManager(db)
    project_manager = ProjectManager(db, analyst_manager)
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
            project_data['userList']
        )
        
        logging.debug(f"Project creation result: {success}")

        if success is None:
            logging.error("Project creation failed")
            raise HTTPException(status_code=500, detail="Project creation failed")

        return {"message": "Project created successfully", "project": project_data}
    except Exception as e:
        logging.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Lock/Unlock a project
@team3_router.put("/projects/{project_name}/lock")
async def lock_project(project_name: str, analyst_id: str):
    print(f"Toggling lock for project {project_name} by analyst {analyst_id}")
    success = project_manager.toggle_project_lock(project_name, analyst_id)
    if success is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project lock state changed successfully", "locked": success}

# ✅ Delete a project (only if unlocked)
@team3_router.delete("/projects/{project_name}/delete")
async def delete_project(project_name: str, analyst_id: str):
    print(f"Delete {project_name} by analyst {analyst_id}")
    success = project_manager.delete_project(analyst_id, project_name)
    if success is None:
        raise HTTPException(status_code=403, detail="Project is locked or does not exist")
    return {"message": "Project deleted successfully"}

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
                "description": project.get("description", ""),
                "start_date": project.get("start_date"),
                "end_date": project.get("end_date"),
                "locked": project.get("locked", False),
                "created_at": project.get("created_at")
            })
            
        return {"projects": formatted_projects}
    except Exception as e:
        logging.error(f"Error fetching analyst projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))