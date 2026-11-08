from importlib.metadata import packages_distributions
import matplotlib.pyplot as plt
import sys
import ast
from pathlib import Path
import networkx as nx
from collections import Counter
project_path = Path(input("Enter the path to a project folder: "))

if not project_path.is_dir():
    print("That folder does not exist.")
else:
    print(f"\nScanning: {project_path.resolve()}\n")

    for item in sorted(project_path.rglob("*")):
        if "venv" in item.parts or ".git" in item.parts:
            continue

        kind = "Folder" if item.is_dir() else "File"
        relative_path = item.relative_to(project_path)
        print(f"{kind}: {relative_path}")
        from collections import Counter

file_types = Counter()

for item in project_path.rglob("*"):
    if item.is_file():
        if "venv" in item.parts or ".git" in item.parts:
            continue

        extension = item.suffix.lower()

        if extension:
            file_types[extension] += 1
        else:
            file_types["No extension"] += 1

print("\n--- Project File Summary ---")

for extension, count in file_types.items():
    print(f"{extension}: {count}")
    language_map = {
    ".py": "Python",
    ".js": "JavaScript",
    ".cpp": "C++",
    ".c": "C",
    ".html": "HTML",
    ".css": "CSS",
    ".java": "Java"
}

function_count = 0
class_count = 0
python_files = set()
dependency_report = {
    "local": {},
    "standard_library": {},
    "external": {}
}

print("\n--- Languages Detected ---")

for extension, count in file_types.items():
    language = language_map.get(extension, "Other")
    print(f"{language}: {count} file(s)")
    standard_library = sys.stdlib_module_names

for item in project_path.rglob("*.py"):
    if "venv" in item.parts or ".git" in item.parts:
        continue

    module_path = item.relative_to(project_path).with_suffix("")

    if module_path.name == "__init__":
        module_path = module_path.parent

    python_files.add(module_path.as_posix().replace("/", "."))


# Build a map of Python module names to their actual file paths

standard_library = sys.stdlib_module_names
third_party_packages = set(packages_distributions().keys())

module_to_file = {}

for item in project_path.rglob("*.py"):

    if "venv" in item.parts or ".git" in item.parts:
        continue

    relative_path = item.relative_to(project_path).as_posix()
    module_path = item.relative_to(project_path).with_suffix("")

    if module_path.name == "__init__":
        module_path = module_path.parent

    module_name = module_path.as_posix().replace("/", ".")

    if module_name not in ("", "."):
        module_to_file[module_name] = relative_path


# Initialize dependency report

dependency_report = {
    "local": {},
    "standard_library": {},
    "external": {},
    "unresolved": {}
}


# Scan Python files

for item in project_path.rglob("*.py"):

    if "venv" in item.parts or ".git" in item.parts:
        continue

    try:
        with open(item, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read())

        file_name = item.relative_to(project_path).as_posix()

        for category in dependency_report:
            dependency_report[category][file_name] = []

        def add_dependency(category, dependency):
            if dependency and dependency not in dependency_report[category][file_name]:
                dependency_report[category][file_name].append(dependency)

        def classify_import(module_name):
            
            if not module_name:
                return "unresolved", None

            # Check whether the exact local module exists
            if module_name in module_to_file:
                return "local", module_to_file[module_name]

            root_module = module_name.split(".")[0]

            # Check standard library
            if root_module in standard_library:
                return "standard_library", module_name

            # Check installed external packages
            if root_module in third_party_packages:
                return "external", module_name

            return "unresolved", module_name

        for node in ast.walk(tree):

            # Handle: import greetings
            # Handle: import utils.helper

            if isinstance(node, ast.Import):

                for alias in node.names:
                    category, dependency = classify_import(alias.name)
                    add_dependency(category, dependency)

            # Handle: from utils import helper
            # Handle: from .helper import format_name

            elif isinstance(node, ast.ImportFrom):

                module_name = node.module

                if node.level > 0:

                    current_parts = item.relative_to(
                        project_path
                    ).with_suffix("").parts[:-1]

                    remove_count = node.level - 1

                    if remove_count > len(current_parts):
                        base_module = ""

                    else:
                        base_parts = current_parts[:len(current_parts) - remove_count]

                        if module_name:
                            base_parts += tuple(module_name.split("."))

                        base_module = ".".join(base_parts)

                else:
                    base_module = module_name or ""

                if not base_module:
                    add_dependency("unresolved", "relative import")
                    continue

                for alias in node.names:

                    imported_module = base_module + "." + alias.name

                    category, dependency = classify_import(imported_module)

                    if category == "local":
                        add_dependency(category, dependency)

                    elif category == "unresolved":

                        target_file = module_to_file.get(base_module)
                        available_names = set()

                        if target_file:
                            target_path = project_path / target_file

                            try:
                                with open(target_path, "r", encoding="utf-8") as source:
                                    target_tree = ast.parse(source.read())

                                for target_node in ast.walk(target_tree):

                                    if isinstance(target_node, (
                                        ast.FunctionDef,
                                        ast.AsyncFunctionDef,
                                        ast.ClassDef
                                    )):
                                        available_names.add(target_node.name)

                                    elif isinstance(target_node, ast.Import):
                                        for target_alias in target_node.names:
                                            available_names.add(
                                                target_alias.asname or target_alias.name.split(".")[0]
                                            )

                                    elif isinstance(target_node, ast.ImportFrom):
                                        for target_alias in target_node.names:
                                            available_names.add(
                                                target_alias.asname or target_alias.name
                                            )

                            except (SyntaxError, UnicodeDecodeError):
                                pass

                        if alias.name in available_names:
                            add_dependency("local", target_file)

                        else:
                            add_dependency("unresolved", imported_module)

                    else:
                        add_dependency(category, dependency)

            # Detect functions and classes

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                print(f"Function: {node.name} | File: {file_name}")

            elif isinstance(node, ast.ClassDef):
                print(f"Class: {node.name} | File: {file_name}")

    except (SyntaxError, UnicodeDecodeError):
        continue
# Create a directed dependency graph
graph = nx.DiGraph()

# Add all Python files as nodes
for item in project_path.rglob("*.py"):
    if "venv" in item.parts or ".git" in item.parts:
        continue

    file_name = item.relative_to(project_path).as_posix()
    graph.add_node(file_name)
# Add dependency relationships as edges
for file, dependencies in dependency_report["local"].items():
    for dependency in dependencies:
        graph.add_edge(file, dependency)

max_degree = max(
    (graph.in_degree(file) for file in graph.nodes()),
    default=0
)

print("\nMost depended-on files:")

for file in graph.nodes():
    if graph.in_degree(file) == max_degree:
        print(file, "->", max_degree, "dependent file(s)")

print("\n--- Change Impact Analysis ---")

target_file = input("Enter the filename to analyse: ").strip()

if target_file not in graph:
    print("File not found in dependency graph.")

else:
    # Reverse the graph to find files depending on the target
    reverse_graph = graph.reverse(copy=False)

    # Find affected files and their dependency distance
    impact_distances = nx.single_source_shortest_path_length(
        reverse_graph, target_file
    )

    # Separate direct and indirect dependencies
    direct_affected = sorted(
        file for file, distance in impact_distances.items()
        if distance == 1
    )

    indirect_affected = sorted(
        [
            (file, distance)
            for file, distance in impact_distances.items()
            if distance > 1
        ],
        key=lambda item: (item[1], item[0])
    )

    total_affected = len(direct_affected) + len(indirect_affected)

    print(f"\nImpact analysis for: {target_file}")

    print("\nDirectly affected files:")

    if direct_affected:
        for file in direct_affected:
            print("→", file)
    else:
        print("None")

    print("\nIndirectly affected files:")

    if indirect_affected:
        for file, distance in indirect_affected:
            print(f"→ {file} (distance: {distance})")
    else:
        print("None")

    print("\n--- Impact Summary ---")
    print("Directly affected:", len(direct_affected))
    print("Indirectly affected:", len(indirect_affected))
    print("Total affected:", total_affected)

    # Create impact path graph

    if total_affected > 0:

        impact_graph = nx.DiGraph()

        # Add the changed file and its impact paths
        impact_graph.add_node(target_file)

        for file in direct_affected:
            impact_graph.add_edge(target_file, file)

        for file, distance in indirect_affected:

            path = nx.shortest_path(
                reverse_graph,
                source=target_file,
                target=file
            )

            nx.add_path(impact_graph, path)

        # Arrange nodes by impact distance
        impact_pos = {}

        for file in impact_graph.nodes():
            distance = nx.shortest_path_length(
                reverse_graph,
                source=target_file,
                target=file
            )

            impact_pos[file] = (distance, -list(impact_graph.nodes()).index(file))

        # Draw impact graph
        plt.figure(figsize=(12, 7))

        nx.draw(
            impact_graph,
            impact_pos,
            with_labels=True,
            node_color=[
                "#2563eb" if file == target_file
                else "#16a34a" if file in direct_affected
                else "#9333ea"
                for file in impact_graph.nodes()
            ],
            node_size=3500,
            font_size=9,
            font_weight="bold",
            font_color="white",
            arrows=True,
            arrowsize=25,
            edge_color="gray",
            width=2
        )

        plt.title(
            f"CHANGE IMPACT PATH | {target_file}",
            fontsize=14,
            fontweight="bold"
        )

        plt.axis("off")
        plt.tight_layout()

        plt.savefig(
            "impact_path.png",
            dpi=300,
            bbox_inches="tight"
        )

        print("\nImpact path graph saved successfully!")

        plt.show()
        
print("\n--- Circular Dependency Check ---")

cycles = list(nx.simple_cycles(graph))

if cycles:
    for cycle in cycles:
        print("Cycle found:", " -> ".join(cycle + [cycle[0]]))
else:
    print("No circular dependencies found.")

print("\n--- Dependency Graph ---")

print("Total files (nodes):", graph.number_of_nodes())
print("Total connections (edges):", graph.number_of_edges())

print("\nConnections:")
for source, target in graph.edges():
    print(source, "->", target)

print("\n--- Dependency Report ---")

for category, files in dependency_report.items():
    print(f"\n{category.upper()} DEPENDENCIES:")

    for file, deps in files.items():
        if deps:
            print(f"\n{file}")

            for dependency in deps:
                print(f"    → {dependency}")

if graph.number_of_nodes() == 0:
    print("\nNo Python files found. Skipping graph visualization.")
else:
    print("\nGenerating dependency graph...")

plt.figure(figsize=(12, 8))
plt.gca().set_facecolor("#1e1e2e")
plt.gcf().set_facecolor("#1e1e2e")
pos = nx.spring_layout(graph, k=1.5, seed=42)

max_degree = max(
    (graph.in_degree(file) for file in graph.nodes()),
    default=0
)

node_colors = [
    plt.cm.Oranges(graph.in_degree(file) / max_degree)
    if max_degree > 0 else "lightblue"
    for file in graph.nodes()
]

nx.draw(
    graph,
    pos,
    with_labels=True,
    node_color = [
    "#2563eb" if file == "main.py"
    else "#16a34a" if file == "greetings.py"
    else "#9333ea" if file.endswith(".py")
    else "#f59e0b"
    for file in graph.nodes()
    ],
    node_size=[
    2500 + graph.in_degree(file) * 1000
    for file in graph.nodes()
    ],
    font_size=8,
    font_weight="bold",
    arrows=True,
    font_color="black",
    edge_color="#a6adc8",
    edgecolors="white",
    linewidths=1.5,
    arrowsize=20,
    width=1.8,
)

plt.title(
    "CODE ARCHAEOLOGIST | DEPENDENCY MAP",
    color="black",
    fontsize=16,
    fontweight="bold",
    pad=20
)

plt.legend(
    handles=[
        plt.Line2D([0], [0], marker="o", color="none",
                   markerfacecolor="#f4a261", markeredgecolor="white",
                   markersize=12, label="Depended-on file"),
        plt.Line2D([0], [0], marker="o", color="none",
                   markerfacecolor="lightblue", markeredgecolor="white",
                   markersize=12, label="Independent file")
    ],
    facecolor="#1e1e2e",
    labelcolor="white",
    edgecolor="white"
)

plt.axis("off")
plt.tight_layout()
plt.savefig("dependency_graph.png", dpi=300, bbox_inches="tight")
print("\nDependency graph saved successfully!")
plt.gcf().canvas.manager.set_window_title("Code Archaeologist")
plt.figtext(
    0.02, 0.02,
    f"Files: {graph.number_of_nodes()} | Dependencies: {graph.number_of_edges()}",
    color="black",
    fontsize=10
)
plt.show()

print("\n--- Dependency Statistics ---")

print("Total files:", graph.number_of_nodes())
print("Total connections:", graph.number_of_edges())

max_degree = max(
    (graph.in_degree(file) for file in graph.nodes()),
    default=0
)

print("\nMost depended-on files:")

for file in graph.nodes():
    if graph.in_degree(file) == max_degree:
        print(file, "->", graph.in_degree(file), "dependent file(s)")

