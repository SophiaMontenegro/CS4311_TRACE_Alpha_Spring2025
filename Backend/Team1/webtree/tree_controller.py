import json
import os
from urllib.parse import urlparse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class WebTreeController:
    def __init__(self, tree_builder):
        # Initializes the controller with the tree builderxs
        self.tree_builder = tree_builder

    def validate_json(self, json_data):
        # Validates that the received JSON contains required fields.
        required_fields = {"path", "severity"}
        if not all(field in json_data for field in required_fields):
            raise ValueError("Invalid JSON: Missing required fields (path, severity)")
        return True

    def determine_operation(self, json_data, current_tree):
        # Determines whether the node should be added or updated.
        for node in current_tree:
            if node["path"] == json_data["path"]:
                if node["severity"] != json_data["severity"]:  # Severity changed
                    json_data["operation"] = "update"
                else:
                    return None  # No change needed
                return json_data

        json_data["operation"] = "add"
        return json_data
    
    def extract_path_from_url(self, url):
        parsed = urlparse(url)
        return parsed.path or "/"

    def build_tree_structure(self, data):
        nodes = {}
        tree = []

        for item in data:
            path = item["path"]
            name = path  # Full path as name
            ip = item.get("ip", "0.0.0.0")
            node_id = ip

            node = {
                "node_id": node_id,
                "name": name,
                "severity": item["severity"],
                "children": []
            }

            nodes[path] = node

        for path, node in nodes.items():
            if path == "/":
                tree.append(node)  # This is the root
                continue

            parent_path = "/".join(path.strip("/").split("/")[:-1])
            parent_path = f"/{parent_path}" if parent_path else "/"

            if parent_path in nodes:
                nodes[parent_path]["children"].append(node)
            else:
                tree.append(node)  # Fallback if no parent exists

        return tree

    def find_node_by_path(self, tree, path):
        for node in tree:
            if node["path"] == path:
                return node
        return None

    def process_tree_update(self, json_input):
        try:
            data_list = json_input if isinstance(json_input, list) else [json_input]
            for json_data in data_list:
                self.validate_json(json_data)

                # Normalize path from URL or plain path
                parsed = urlparse(json_data["path"])
                if parsed.scheme and parsed.netloc:
                    json_data["path"] = parsed.path or "/"

                current_tree = self.tree_builder.fetch_tree()
                update_data = self.determine_operation(json_data, current_tree)

                if update_data:
                    self.tree_builder.process_update(json.dumps(update_data))   

                else:
                    print("No update needed.")
                    if "severity" in json_data:
                        node_found = self.find_node_by_path(current_tree, json_data["path"])
                        if node_found:
                            self.tree_builder.update_severity(json_data["path"], json_data["severity"])
                            print(f"Severity updated for {json_data['path']}")

            # Refresh and save updated tree to file (always)
            updated_tree = self.tree_builder.fetch_tree()
            formatted_tree = self.build_tree_structure(updated_tree)
            file_path = os.path.join(BASE_DIR, "../../../Frontend/static/webtree/dummy_tree.json")
            with open(file_path, "w") as file:
                json.dump(formatted_tree, file, indent=2)
            print(f"Updated tree saved to {file_path}")

        except ValueError as e:
            print(f"Error: {e}")
        except json.JSONDecodeError:
            print("Invalid JSON format.")
        except Exception as e:
            print(f"Unexpected error: {e}")
