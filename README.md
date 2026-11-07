# 🔍 Code Archaeologist

**Explore, understand, and analyze unfamiliar codebases.**

Code Archaeologist is a Python-based static code analysis tool designed to help developers understand the internal structure of a software project. It scans project directories, identifies Python components, analyzes dependencies, and visualizes how files are connected.

The goal is to make navigating unfamiliar codebases easier and to understand how changes in one file can affect other parts of a project.

## ✨ Features

- **Project Scanning:** Recursively scans project directories and identifies supported file types.
- **Language Detection:** Counts files based on their extensions.
- **Code Structure Analysis:** Identifies Python functions, asynchronous functions, and classes using Python AST.
- **Dependency Classification:** Categorizes imports into local, standard library, external, and unresolved dependencies.
- **Dependency Mapping:** Builds a directed graph showing relationships between Python files.
- **Change Impact Analysis:** Identifies files that may be affected when a particular file changes.
- **Impact Path Visualization:** Displays direct and indirect impact paths.
- **Circular Dependency Detection:** Checks for circular dependencies.
- **Connectivity Analysis:** Identifies highly connected and frequently depended-on files.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| AST | Static code analysis |
| NetworkX | Dependency graph construction and analysis |
| Matplotlib | Graph visualization |
| pathlib | Project directory scanning |
| collections.Counter | File statistics |

## 📂 Project Structure

```text
code-archaeologist/
│
├── main.py
├── .gitignore
├── README.md
│
├── sample_project/
│   ├── calculator.py
│   ├── greetings.py
│   ├── main.py
│   └── utils/
│       ├── __init__.py
│       └── helper.py
│
└── venv/                 # Excluded from Git
```

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/code-archaeologist.git
cd code-archaeologist
```

**2. Install dependencies**

```bash
pip install networkx matplotlib
```

**3. Run the application**

```bash
python main.py
```

**4. Enter the path of the project you want to analyze** when prompted.

## 📊 Visualizations

Code Archaeologist generates two important visualizations:

**1. Dependency Map**

Displays the relationships between Python files and shows which files depend on other files.

**2. Change Impact Path**

Highlights the files that may be affected by changes to a selected file, distinguishing direct and indirect impacts.

The generated visualizations are saved as:

- `dependency_graph.png`
- `impact_path.png`

## 🧠 How It Works

1. The project directory is scanned using Python's `pathlib`.
2. Python files are parsed using the Abstract Syntax Tree (AST).
3. Imports are identified and classified.
4. A directed dependency graph is constructed using NetworkX.
5. Graph algorithms are used to analyze dependencies, cycles, and change impact.
6. Matplotlib generates visual representations of the results.

## 🚀 Future Improvements

- Interactive web-based dashboard.
- GitHub repository integration.
- Advanced dependency resolution.
- Improved support for multiple programming languages.
- More detailed code complexity analysis.
- Interactive exploration of dependency graphs.

## 🎯 Project Objective

The objective of Code Archaeologist is to simplify codebase exploration and provide developers with a better understanding of software structure, dependencies, and potential change impact.

**Built with Python, curiosity, and a passion for understanding how code works.**