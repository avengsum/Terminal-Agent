import os
import json
from typing import Dict, List, Optional
from pathlib import Path

def detect_project_type() -> str:
    """
    Detect the type of project based on config files.
    Returns: 'python', 'javascript', 'typescript', 'java', 'unknown'
    """
    cwd = os.getcwd()
    
    # Check for Python
    if os.path.exists(os.path.join(cwd, "requirements.txt")) or \
       os.path.exists(os.path.join(cwd, "setup.py")) or \
       os.path.exists(os.path.join(cwd, "pyproject.toml")) or \
       os.path.exists(os.path.join(cwd, "Pipfile")):
        return "python"
    
    # Check for JavaScript/TypeScript
    if os.path.exists(os.path.join(cwd, "package.json")):
        with open(os.path.join(cwd, "package.json"), "r") as f:
            try:
                pkg = json.load(f)
                if "typescript" in pkg.get("devDependencies", {}) or \
                   os.path.exists(os.path.join(cwd, "tsconfig.json")):
                    return "typescript"
                return "javascript"
            except:
                return "javascript"
    
    # Check for Java
    if os.path.exists(os.path.join(cwd, "pom.xml")) or \
       os.path.exists(os.path.join(cwd, "build.gradle")):
        return "java"
    
    # Check for Go
    if os.path.exists(os.path.join(cwd, "go.mod")):
        return "go"
    
    # Check for Rust
    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        return "rust"
    
    return "unknown"


def get_project_structure() -> Dict:
    """
    Analyze and return project structure.
    Returns dict with project info.
    """
    cwd = os.getcwd()
    structure = {
        "type": detect_project_type(),
        "root": cwd,
        "config_files": [],
        "source_dirs": [],
        "test_dirs": [],
        "entry_points": []
    }
    
    # Find config files
    config_patterns = [
        "package.json", "requirements.txt", "setup.py", "pyproject.toml",
        "tsconfig.json", "pom.xml", "build.gradle", "go.mod", "Cargo.toml",
        ".gitignore", "README.md", "Dockerfile", "docker-compose.yml"
    ]
    
    for pattern in config_patterns:
        path = os.path.join(cwd, pattern)
        if os.path.exists(path):
            structure["config_files"].append(pattern)
    
    # Find source directories (common patterns)
    common_src_dirs = ["src", "lib", "app", "main", "source"]
    common_test_dirs = ["tests", "test", "__tests__", "spec"]
    
    for item in os.listdir(cwd):
        item_path = os.path.join(cwd, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            if item.lower() in common_src_dirs:
                structure["source_dirs"].append(item)
            elif item.lower() in common_test_dirs:
                structure["test_dirs"].append(item)
    
    # Find entry points
    entry_patterns = {
        "python": ["main.py", "app.py", "run.py", "manage.py", "__main__.py"],
        "javascript": ["index.js", "app.js", "server.js", "main.js"],
        "typescript": ["index.ts", "app.ts", "server.ts", "main.ts"]
    }
    
    project_type = structure["type"]
    if project_type in entry_patterns:
        for pattern in entry_patterns[project_type]:
            path = os.path.join(cwd, pattern)
            if os.path.exists(path):
                structure["entry_points"].append(pattern)
    
    return structure


def get_dependencies() -> Dict:
    """
    Get project dependencies based on project type.
    Returns dict with dependencies info.
    """
    cwd = os.getcwd()
    deps = {
        "runtime": [],
        "dev": [],
        "file": None
    }
    
    project_type = detect_project_type()
    
    if project_type == "python":
        # Try requirements.txt
        req_file = os.path.join(cwd, "requirements.txt")
        if os.path.exists(req_file):
            deps["file"] = "requirements.txt"
            try:
                with open(req_file, "r") as f:
                    deps["runtime"] = [line.strip() for line in f 
                                      if line.strip() and not line.startswith("#")]
            except:
                pass
        
        # Try pyproject.toml
        pyproject = os.path.join(cwd, "pyproject.toml")
        if os.path.exists(pyproject):
            deps["file"] = "pyproject.toml"
            # Basic parsing (could use tomli for better parsing)
            try:
                with open(pyproject, "r") as f:
                    content = f.read()
                    # Simple extraction (not perfect but works)
                    if "[project]" in content or "[tool.poetry.dependencies]" in content:
                        deps["runtime"] = ["See pyproject.toml for details"]
            except:
                pass
    
    elif project_type in ["javascript", "typescript"]:
        pkg_file = os.path.join(cwd, "package.json")
        if os.path.exists(pkg_file):
            deps["file"] = "package.json"
            try:
                with open(pkg_file, "r") as f:
                    pkg = json.load(f)
                    deps["runtime"] = list(pkg.get("dependencies", {}).keys())
                    deps["dev"] = list(pkg.get("devDependencies", {}).keys())
            except:
                pass
    
    return deps


def find_config_files() -> List[str]:
    """Find all configuration files in the project."""
    cwd = os.getcwd()
    config_files = []
    
    patterns = [
        "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg",
        "*.config.js", "*.config.ts", "Dockerfile", ".gitignore",
        ".env.example", "requirements*.txt", "package.json", "tsconfig.json"
    ]
    
    for root, dirs, files in os.walk(cwd):
        # Skip hidden directories and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.venv']]
        
        for file in files:
            for pattern in patterns:
                if file.endswith(tuple(pattern.replace('*', '').split('.'))):
                    rel_path = os.path.relpath(os.path.join(root, file), cwd)
                    config_files.append(rel_path)
                    break
    
    return sorted(config_files)


def find_entry_points() -> List[str]:
    """Find potential entry points for the project."""
    cwd = os.getcwd()
    entry_points = []
    
    project_type = detect_project_type()
    
    if project_type == "python":
        patterns = ["main.py", "app.py", "run.py", "manage.py", "__main__.py", "cli.py"]
    elif project_type in ["javascript", "typescript"]:
        patterns = ["index.js", "index.ts", "app.js", "app.ts", "server.js", "server.ts", "main.js", "main.ts"]
    else:
        return []
    
    for pattern in patterns:
        path = os.path.join(cwd, pattern)
        if os.path.exists(path):
            entry_points.append(pattern)
    
    # Also check common directories
    for src_dir in ["src", "app", "main"]:
        src_path = os.path.join(cwd, src_dir)
        if os.path.isdir(src_path):
            for pattern in patterns:
                path = os.path.join(src_path, pattern)
                if os.path.exists(path):
                    rel_path = os.path.relpath(path, cwd)
                    entry_points.append(rel_path)
    
    return entry_points


def get_project_info() -> str:
    """
    Get comprehensive project information as a formatted string.
    Useful for providing context to the AI agent.
    """
    structure = get_project_structure()
    deps = get_dependencies()
    
    info = f"""
Project Type: {structure['type'].upper()}
Root Directory: {structure['root']}

Config Files Found:
{chr(10).join('  - ' + f for f in structure['config_files'])}

Source Directories:
{chr(10).join('  - ' + d for d in structure['source_dirs']) if structure['source_dirs'] else '  (none found)'}

Test Directories:
{chr(10).join('  - ' + d for d in structure['test_dirs']) if structure['test_dirs'] else '  (none found)'}

Entry Points:
{chr(10).join('  - ' + e for e in structure['entry_points']) if structure['entry_points'] else '  (none found)'}

Dependencies:
  File: {deps['file'] or 'Not found'}
  Runtime: {len(deps['runtime'])} packages
  Dev: {len(deps['dev'])} packages
"""
    
    return info.strip()
