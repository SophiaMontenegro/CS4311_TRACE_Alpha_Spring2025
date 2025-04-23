class InteractiveUI:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.commands = {
            "create lead": self.create_lead_analyst,
            "show projects": self.show_projects,
            "create project": self.create_project,
            "exit": self.exit_program,
        }

    def start(self):
        print("Connected to Neo4j database. Type a command to begin or 'exit' to close.")
        print("Available commands: create lead, show projects, create project, exit")

        while True:
            query = input("neo4j> ").strip().lower()

            if query in self.commands:
                self.commands[query]()
            else:
                print("Invalid command. Please enter 'create lead', 'show projects', 'create project', or 'exit'.")

    def create_lead_analyst(self):
        print("Type Name and Id separated by a comma (or type 'exit' to cancel)")
        query = input("neo4j> ").strip()
        if query.lower() == 'exit':
            return
        try:
            name, id_ = map(str.strip, query.split(","))
            self.db_manager.create_LeadAnalyst(name, id_)
        except ValueError:
            print("Invalid input. Please enter Name and ID separated by a comma.")

    def show_projects(self):
        print("Type the initials of Lead Analyst for specific projects or leave blank to see all projects (or type 'exit' to cancel)")
        query = input("neo4j> ").strip()
        if query.lower() == 'exit':
            return
        results = self.db_manager.show_projects(query if query else None)
        for record in results:
            print(record)

    def create_project(self):
        print("Type Id of project, Name of project, and owner of the project separated by commas in that order (or type 'exit' to cancel)")
        query = input("neo4j> ").strip()
        if query.lower() == 'exit':
            return
        try:
            id_, name, owner = map(str.strip, query.split(","))
            self.db_manager.create_projects(owner, name, id_)
        except ValueError:
            print("Invalid input. Please enter Project ID, Project Name, and Owner separated by commas.")

    def exit_program(self):
        print("Closing...")
        self.db_manager.close()
        exit()