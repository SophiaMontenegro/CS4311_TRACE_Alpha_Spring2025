# db_config.py - Handles database configurations securely

import os
from dotenv import load_dotenv

class DatabaseConfig:
    """Handles loading database configurations from environment variables."""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve database configurations from environment variables
        self.DB_URI = os.getenv("NEO4J_URI")  # No default value, must be in .env
        self.DB_USER = os.getenv("NEO4J_USER")
        self.DB_PASSWORD = os.getenv("NEO4J_PASSWORD")

        # Optional: Raise an error if any value is missing
        if not all([self.DB_URI, self.DB_USER, self.DB_PASSWORD]):
            raise ValueError("Database configuration is incomplete. Check your .env file.")

    def get_config(self):
        """Returns database connection details as a dictionary."""
        return {
            "uri": self.DB_URI,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
        }

# Usage example
if __name__ == "__main__":
    env = DatabaseConfig()
    print(env.get_config())  # Print database settings (for debugging)
