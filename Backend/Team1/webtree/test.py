import json
from tree_builder import WebTreeBuilder
from tree_controller import WebTreeController

# Initialize builder and controller
tree_builder = WebTreeBuilder("bolt://localhost:7687", "neo4j", "chrischris21")
controller = WebTreeController(tree_builder)

# Sample array of attack input JSONs
json_samples = [
    # Visible tree structure
    {"ip": "198.51.100.1", "path": "https://example.com/", "severity": "root"},
    {"ip": "198.51.100.3", "path": "https://example.com/help", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/home", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/metrics", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/home/dashboard/settings", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/about", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/about/team/members", "severity": "low"},

    # Hidden nodes (their parents are missing from the tree)
    {"ip": "198.51.100.1", "path": "https://example.com/about/company/history", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/login/reset", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/register/validate", "severity": "low"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/cloud/compute", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/services/ai/nlp", "severity": "medium"},
    {"ip": "198.51.100.1", "path": "https://example.com/contact/sales", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/blog/posts/trending", "severity": "high"},
    {"ip": "198.51.100.1", "path": "https://example.com/faq/security/test", "severity": "high"}
]

# Run batch update
print("\nProcessing JSON Array:")
controller.process_tree_update(json_samples)

# Verify tree
print("\nTree Structure After Batch Update:")
final_tree = tree_builder.fetch_tree()
for node in final_tree:
    print(node)

tree_builder.close()
