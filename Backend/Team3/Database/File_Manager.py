import os
import logging

class FileManager:
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

            return True  # Indicate success

        except Exception as e:
            logging.error(f"Error creating folders for project: {e}", exc_info=True)
            return None

