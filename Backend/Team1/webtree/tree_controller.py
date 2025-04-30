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
        for node in current_tree:
            if node.get("path") == json_data.get("path"):
                current_sev = node.get("severity", "unknown")
                incoming_sev = json_data.get("severity", "unknown")

                print(f"Comparing for {node['path']}: current='{current_sev}', incoming='{incoming_sev}'")

                if current_sev != incoming_sev:
                    json_data["operation"] = "update"
                    return json_data
                else:
                    return None
        json_data["operation"] = "add"
        return json_data


    
    def extract_path_from_url(self, url):
        parsed = urlparse(url)
        return parsed.path or "/"

    def build_tree_structure(self, data):
        visible_tree = []
        hidden_root = {
            "node_id": "hidden",
            "name": "Hidden",
            "severity": "low",
            "hidden": True,
            "children": []
        }

        nodes = {}

        # Preload root node if it's in the data to allow child inference
        for item in data:
            if item["path"] == "/":
                nodes["/"] = {
                    "node_id": item.get("ip", "0.0.0.0"),
                    "name": "/",
                    "severity": item.get("severity", "unknown"),
                    "children": [],
                    "hidden": item.get("hidden", False),
                    "url": item.get("url", "")
                }
                break


        # Build node map
        for item in data:
            path = item["path"]
            name = path
            ip = item.get("ip", "0.0.0.0")
            node_id = ip
            hidden = item.get("hidden", False)
            url = item.get("url") or self.infer_url(path, nodes)

            node = {
                "node_id": node_id,
                "name": name,
                "severity": item.get("severity", "unknown"),
                "children": [],
                "hidden": hidden,
                "url": url
            }

            nodes[path] = node

        # Build tree structure
        for path, node in nodes.items():
            parent_path = "/".join(path.strip("/").split("/")[:-1])
            parent_path = f"/{parent_path}" if parent_path else "/"
            parent = nodes.get(parent_path)

            if node["hidden"]:
                # Nest under hidden parent, or under the synthetic hidden root
                if parent and parent.get("hidden") == True:
                    parent["children"].append(node)
                else:
                    hidden_root["children"].append(node)
            else:
                if path == "/":
                    visible_tree.append(node)
                elif parent:
                    parent["children"].append(node)
                else:
                    visible_tree.append(node)

        return {
            "visible": visible_tree,
            "hidden": [hidden_root] if hidden_root["children"] else []
        }
    
    def infer_url(self, path, nodes):
        parent_path = "/".join(path.strip("/").split("/")[:-1])
        parent_path = f"/{parent_path}" if parent_path else "/"
        parent_node = nodes.get(parent_path)

        if parent_node and parent_node.get("url"):
            base = parent_node["url"].rstrip("/")
            suffix = path.split("/")[-1]
            inferred = f"{base}/{suffix}"
            print(f"Inferred URL for {path}: {inferred}")
            return inferred

        print(f"No URL found for {path}")
        return ""


    
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

                current_tree = self.tree_builder.fetch_tree()
                update_data = self.determine_operation(json_data, current_tree)

                # Only parse the path *after* checking severity
                parsed = urlparse(json_data["path"])
                if parsed.scheme and parsed.netloc:
                    json_data["path"] = parsed.path or "/"


                current_tree = self.tree_builder.fetch_tree()
                update_data = self.determine_operation(json_data, current_tree)
                print("Resolved operation:", update_data.get("operation") if update_data else "none")


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
            self.tree_builder.backfill_missing_urls()

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