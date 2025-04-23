import json
import os
from urllib.parse import urlparse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class WebTreeController:
    def __init__(self, tree_builder):
        # Initializes the controller with the tree builderxs
        self.tree_builder = tree_builder

    def validate_json(self, json_data):
        if "path" not in json_data:
            raise ValueError("Invalid JSON: Missing required field 'path'")
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


        nodes = {}
        tree = []

        hidden_group = {
            "node_id": "hidden",
            "name": "Hidden Nodes",
            "severity": "low",
            "children": [],
        }

    def build_tree_structure(self, data):
        visible_tree = []
        hidden_tree = []
        nodes = {}

        for item in data:
            path = item["path"]
            name = path
            ip = item.get("ip", "0.0.0.0")
            node_id = ip
            hidden = item.get("hidden", False)

            node = {
                "node_id": node_id,
                "name": name,
                "severity": item["severity"],
                "children": [],
                "hidden": hidden
            }

            nodes[path] = node

        for path, node in nodes.items():
            if node["hidden"]:
                hidden_tree.append(node)
                continue

            if path == "/":
                visible_tree.append(node)
                continue

            parent_path = "/".join(path.strip("/").split("/")[:-1])
            parent_path = f"/{parent_path}" if parent_path else "/"

            if parent_path in nodes:
                nodes[parent_path]["children"].append(node)
            else:
                visible_tree.append(node)

        return {
            "visible": visible_tree,
            "hidden": hidden_tree
        }

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

            # Save visible
            with open(os.path.join(BASE_DIR, "../../../Frontend/static/webtree/dummy_tree.json"), "w") as f:
                json.dump(formatted_tree["visible"], f, indent=2)

            # Save hidden
            with open(os.path.join(BASE_DIR, "../../../Frontend/static/webtree/hidden_tree.json"), "w") as f:
                json.dump(formatted_tree["hidden"], f, indent=2)

            print("Updated trees saved.")

        except ValueError as e:
            print(f"Error: {e}")
        except json.JSONDecodeError:
            print("Invalid JSON format.")
        except Exception as e:
            print(f"Unexpected error: {e}")
