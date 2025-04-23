from outdated.Database_ import DatabaseManager
from ui import InteractiveUI
from config import DatabaseConfig # old class

if __name__ == "__main__":

    try:
        env = DatabaseConfig()
        db_manager = DatabaseManager(env)
        ui = InteractiveUI(db_manager)
        ui.start()

    except Exception as e:
        print(f"Database connection test failed ❌: {e}")
