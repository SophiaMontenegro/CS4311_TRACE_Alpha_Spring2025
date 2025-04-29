import os
import logging
from datetime import datetime

class FileManager:
    def __init__(self, db_manager):
        self.db = db_manager
    def is_valid_path(self, filePath):
        return isinstance(filePath, str) and filePath.strip()

    def ensure_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            logging.debug(f"Created Directory: {path}")
        else:
            logging.debug(f"Directory Already Exists: {path}")

    def fileCreation(self, project_name, filePath):
        tools = [
            "BruteForce", "Crawler", "Fuzzer", "Gen_AI",
            "HTTP", "Intruder", "SQLInjection", "WebTree"
        ]

        if not self.is_valid_path(filePath):
            logging.error("Invalid file path: Path must be a non-empty string.")
            return None

        try:
            # Create the project folder inside the base path
            project_folder = os.path.join(filePath, project_name)
            self.ensure_directory(project_folder)

            for tool in tools:
                toolPath = os.path.join(project_folder, tool)  # <- updated line
                self.ensure_directory(toolPath)

            # Create the nodes in the db

            return True  # Indicate success

        except Exception as e:
            logging.error(f"Error creating folders for project: {e}", exc_info=True)
            return None



    def create_file_node(self, project_name, job_id, file_name, file_path, size=None, is_log=False, file_format="csv"):
        query = """
        MATCH (p:Project {name: $project_name})
        CREATE (f:File {
            file_name: $file_name,
            path: $file_path,
            job_id: $job_id,
            created: datetime(),
            modified: datetime(),
            size: $size,
            is_log: $is_log,
            format: $file_format
        })
        CREATE (p)-[:HAS_FILE]->(f)
        """

        try:
            self.db.run_query(query, {
                "project_name": project_name,
                "job_id": job_id,
                "file_name": file_name,
                "file_path": file_path,
                "size": size,
                "is_log": is_log,
                "file_format": file_format
            })
            return True
        except Exception as e:
            logging.error(f"Error creating file node for project '{project_name}': {e}", exc_info=True)
            return None



    def get_file_info(self, project_name, job_id, file_type, file_path):
        """
        Retrieves file metadata for a given project, job_id, file type, and file path
        based on the updated relationship from Project -> Tool -> File.
        """
        query = """
        MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool {name: $file_type})-[:HAS_FILE]->(f:File)
        WHERE f.job_id = $job_id AND f.path = $file_path
        RETURN f.path AS path,
               f.type AS type,
               f.job_id AS job_id,
               f.created AS created,
               f.modified AS modified,
               f.size AS size,
               f.is_log AS is_log,
               f.format AS format
        """
        return self.db.run_query(query, {
            "project_name": project_name,
            "job_id": job_id,
            "file_type": file_type,
            "file_path": file_path
        }, fetch=True)

    def get_all_job_ids_by_tool(self, project_name):
        """
        Retrieves all job IDs grouped by tool for a given project.
        Returns a dictionary of the form:
        {
            "Crawler": [(job_id1, created_date1), (job_id2, created_date2)],
            "SQLInjection": [(job_id1, created_date1), ...],
            ...
        }
        """
        query = """
        MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool)-[:HAS_FILE]->(f:File)
        WHERE f.job_id IS NOT NULL AND f.job_id <> "" AND f.job_id <> "webtree"
        RETURN t.name AS tool, f.job_id AS job_id, f.created AS created
        ORDER BY t.name, f.created
        """
        results = self.db.run_query(query, {
            "project_name": project_name
        }, fetch=True)

        job_map = {}
        for record in results:
            tool = record["tool"]
            job_id = record["job_id"]
            created = record.get("created")
            if tool not in job_map:
                job_map[tool] = []
            job_map[tool].append((job_id, created))

        return job_map

    def scan_and_register_files(self, base_directory, project_name):
        """
        Scans tool folders under the specified project directory and registers file nodes.
        Associates each file with its respective Tool node and updates Tool node with job_ids.
        """
        if not os.path.isdir(base_directory):
            return

        for tool_dir in os.listdir(base_directory):
            tool_path = os.path.join(base_directory, tool_dir)
            if not os.path.isdir(tool_path):
                continue

            # Normalize tool name to match Tool node formatting (e.g., BruteForce, SQLInjection)
            tool_name = tool_dir.replace("_", " ").title().replace(" ", "")

            for root, _, files in os.walk(tool_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    stat = os.stat(file_path)
                    job_id = self._extract_job_id(file)
                    created = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    size = stat.st_size

                    ext = os.path.splitext(file)[1].lower()
                    file_format = "csv" if ext == ".csv" else "json" if ext == ".json" else ext
                    is_log = "_log_" in file or "_logs_" in file

                    # Special handling for web_tree which has no job ID
                    if tool_name.lower() == "webtree":
                        job_id = "webtree"

                    # Create file node and relationship to Tool
                    self.create_file_node(project_name, job_id, tool_name, file_path, created, modified, size, is_log, file_format)

                    # Relate file to Tool
                    relate_file_query = """
                    MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool {name: $tool_name}),
                          (f:File {path: $file_path})
                    MERGE (t)-[:HAS_FILE]->(f)
                    """
                    self.db.run_query(relate_file_query, {
                        "project_name": project_name,
                        "tool_name": tool_name,
                        "file_path": file_path
                    })

                    # Append job_id to tool node
                    self.append_job_id_to_tool(project_name, tool_name, job_id)

    def append_job_id_to_tool(self, project_name, tool_name, job_id):
        """
        Appends a job_id to the job_ids list in the Tool node for a given project and tool.
        Ensures no duplicates are added.
        Returns True on success, False on failure.
        """
        query = """
        MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool {name: $tool_name})
        SET t.job_ids = coalesce(t.job_ids, []) + CASE WHEN $job_id IN t.job_ids THEN [] ELSE [$job_id] END
        """
        try:
            self.db.run_query(query, {
                "project_name": project_name,
                "tool_name": tool_name,
                "job_id": job_id
            })
            return True
        except Exception as e:
            logging.error(f"Error appending job_id to tool '{tool_name}': {e}", exc_info=True)
            return False


    def extract_job_id(self, filename):
        """
        Extracts a job ID from a filename using the new convention:
        <tool>_results_<jobid>.json -> returns <jobid>
        Example: 'fuzzer_results_abcd1234.json' -> 'abcd1234'
        """
        if "_results_" in filename:
            try:
                return filename.split("_results_")[1].split(".")[0]
            except IndexError:
                return "unknown"
        return "unknown"

    def get_result_files(self, project_name, tool_name, job_id):
        """
        Retrieves result file metadata for a given project, tool, and job_id (excluding logs).
        """
        query = """
        MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool {name: $tool_name})-[:HAS_FILE]->(f:File)
        WHERE f.job_id = $job_id AND f.is_log = false
        RETURN f.path AS path,
               f.job_id AS job_id,
               f.format AS format,
               f.size AS size,
               f.created AS created,
               f.modified AS modified
        """
        return self.db.run_query(query, {
            "project_name": project_name,
            "tool_name": tool_name,
            "job_id": job_id
        }, fetch=True)

    def get_tool_directory(self, project_name, tool_name):
        """
        Retrieves the directory attribute of a specific tool associated with a project.
        """
        query = """
        MATCH (p:Project {name: $project_name})-[:ToolResults]->(t:Tool {name: $tool_name})
        RETURN t.file_path AS file_path
        """
        result = self.db.run_query(query, {
            "project_name": project_name,
            "tool_name": tool_name
        }, fetch=True)
        print("✅ Result:", result)
        return result[0]["file_path"] if result and result[0].get("file_path") else None

    def create_tools_for_project(self, project_name: str, base_file_path: str):
        """
        Creates Tool nodes for a project, appending the tool name to the file_path,
        and initializing an empty job_ids list.

        Parameters:
        - project_name: The name of the project
        - base_file_path: The base path where each tool directory will be appended
        """
        tools = [
            "BruteForce",
            "Crawler",
            "Fuzzer",
            "Gen_AI",
            "HTTP",
            "Intruder",
            "SQLInjection",
            "WebTree"
        ]

        tool_nodes = []
        for tool_name in tools:
            full_path = f"{base_file_path}\\{project_name}\\{tool_name}"  # Windows-style path
            tool_nodes.append({
                "name": tool_name,
                "file_path": full_path,
                "job_ids": []
            })

        query = """
        MATCH (p:Project {name: $project_name})
        UNWIND $tool_nodes AS tool
        CREATE (t:Tool {
            name: tool.name,
            file_path: tool.file_path,
            job_ids: tool.job_ids
        })
        CREATE (p)-[:ToolResults]->(t)
        """

        try:
            self.db.run_query(query, {
                "project_name": project_name,
                "tool_nodes": tool_nodes
            })
            logging.debug(f"Successfully created tool nodes for project {project_name} with paths.")
            return True
        except Exception as e:
            logging.error(f"Error creating tools for project '{project_name}': {e}", exc_info=True)
            return False



