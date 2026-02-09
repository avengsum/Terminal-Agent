import os
import ast
import re
from typing import Dict, List, Optional, Set
from collections import defaultdict

class CodebaseIndex:
    """Index codebase to understand structure and relationships."""
    
    def __init__(self):
        self.functions = {}  # {file_path: [function_info]}
        self.classes = {}    # {file_path: [class_info]}
        self.imports = {}    # {file_path: [imports]}
        self.function_calls = defaultdict(list)  # {function_name: [caller_files]}
        self.file_dependencies = defaultdict(set)  # {file: {imported_files}}
    
    def index_file(self, file_path: str) -> Dict:
        """
        Index a single Python file.
        Returns dict with extracted information.
        """
        if not file_path.endswith('.py'):
            return {"error": "Only Python files supported currently"}
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            file_info = {
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            # Extract functions, classes, and imports
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(node, 'end_lineno', node.lineno),
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else []
                    }
                    file_info["functions"].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(node, 'end_lineno', node.lineno),
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "bases": [ast.unparse(b) for b in node.bases] if hasattr(ast, 'unparse') else []
                    }
                    file_info["classes"].append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports = [alias.name for alias in node.names]
                    else:
                        module = node.module or ""
                        imports = [f"{module}.{alias.name}" if module else alias.name 
                                  for alias in node.names]
                    file_info["imports"].extend(imports)
            
            # Store in index
            self.functions[file_path] = file_info["functions"]
            self.classes[file_path] = file_info["classes"]
            self.imports[file_path] = file_info["imports"]
            
            return file_info
        
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error indexing file: {str(e)}"}
    
    def index_project(self, root_dir: Optional[str] = None, max_files: int = 100) -> Dict:
        """
        Index entire project.
        
        Args:
            root_dir: Root directory to index (defaults to current dir)
            max_files: Maximum number of files to index
        
        Returns:
            Summary of indexing results
        """
        if root_dir is None:
            root_dir = os.getcwd()
        
        indexed = 0
        errors = []
        
        for root, dirs, files in os.walk(root_dir):
            # Skip hidden and common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['__pycache__', 'node_modules', 'venv', '.venv', 'build', 'dist']]
            
            for file in files:
                if indexed >= max_files:
                    break
                
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = self.index_file(file_path)
                    
                    if "error" not in result:
                        indexed += 1
                    else:
                        errors.append(f"{file_path}: {result['error']}")
        
        return {
            "indexed_files": indexed,
            "total_functions": sum(len(funcs) for funcs in self.functions.values()),
            "total_classes": sum(len(classes) for classes in self.classes.values()),
            "errors": errors[:10]  # Limit error output
        }
    
    def find_function(self, function_name: str) -> List[Dict]:
        """
        Find all definitions of a function.
        
        Returns:
            List of function definitions with file and line info
        """
        results = []
        
        for file_path, functions in self.functions.items():
            for func in functions:
                if func["name"] == function_name:
                    results.append({
                        "file": file_path,
                        "name": func["name"],
                        "line": func["line"],
                        "args": func["args"]
                    })
        
        return results
    
    def find_class(self, class_name: str) -> List[Dict]:
        """Find all definitions of a class."""
        results = []
        
        for file_path, classes in self.classes.items():
            for cls in classes:
                if cls["name"] == class_name:
                    results.append({
                        "file": file_path,
                        "name": cls["name"],
                        "line": cls["line"],
                        "methods": cls["methods"]
                    })
        
        return results
    
    def find_usages(self, name: str) -> List[str]:
        """
        Find files that import or use a function/class.
        Simple text-based search (could be enhanced with AST).
        """
        usages = []
        
        for file_path in self.functions.keys():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check imports
                if name in self.imports.get(file_path, []):
                    usages.append(f"{file_path} (imported)")
                
                # Check usage in code (simple pattern match)
                pattern = rf'\b{re.escape(name)}\s*\('
                if re.search(pattern, content):
                    usages.append(f"{file_path} (used)")
            
            except:
                continue
        
        return list(set(usages))
    
    def get_file_dependencies(self, file_path: str) -> List[str]:
        """Get files that this file imports (local imports only)."""
        if file_path not in self.imports:
            return []
        
        dependencies = []
        imports = self.imports[file_path]
        
        # Find local imports (files in the project)
        for imp in imports:
            # Convert import to potential file path
            if '.' in imp:
                parts = imp.split('.')
                # Try to find corresponding .py file
                potential_path = os.path.join(*parts) + '.py'
                if os.path.exists(potential_path):
                    dependencies.append(potential_path)
        
        return dependencies
    
    def find_related_files(self, file_path: str) -> List[str]:
        """
        Find files related to the given file.
        Includes files that import it, files it imports, and files with similar names.
        """
        related = set()
        
        # Files this file imports
        related.update(self.get_file_dependencies(file_path))
        
        # Files that import this file
        file_name = os.path.basename(file_path).replace('.py', '')
        for other_file, imports in self.imports.items():
            for imp in imports:
                if file_name in imp or file_path in imp:
                    related.add(other_file)
        
        return list(related)


# Global instance
_indexer = CodebaseIndex()

def index_project(root_dir: Optional[str] = None) -> str:
    """Index the project and return summary."""
    result = _indexer.index_project(root_dir)
    return f"""Indexed {result['indexed_files']} files
Found {result['total_functions']} functions
Found {result['total_classes']} classes
"""

def find_function(function_name: str) -> str:
    """Find function definitions."""
    results = _indexer.find_function(function_name)
    
    if not results:
        return f"Function '{function_name}' not found"
    
    output = [f"Found {len(results)} definition(s) of '{function_name}':"]
    for r in results:
        output.append(f"  - {r['file']}:{r['line']} ({', '.join(r['args'])})")
    
    return "\n".join(output)

def find_usages(name: str) -> str:
    """Find where a function/class is used."""
    usages = _indexer.find_usages(name)
    
    if not usages:
        return f"No usages found for '{name}'"
    
    return f"Found {len(usages)} usage(s) of '{name}':\n" + "\n".join(f"  - {u}" for u in usages)

def get_file_dependencies(file_path: str) -> str:
    """Get dependencies of a file."""
    deps = _indexer.get_file_dependencies(file_path)
    
    if not deps:
        return f"No local dependencies found for {file_path}"
    
    return f"Dependencies of {file_path}:\n" + "\n".join(f"  - {d}" for d in deps)

def find_related_files(file_path: str) -> str:
    """Find files related to the given file."""
    related = _indexer.find_related_files(file_path)
    
    if not related:
        return f"No related files found for {file_path}"
    
    return f"Related files for {file_path}:\n" + "\n".join(f"  - {r}" for r in related)
