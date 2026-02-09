import os
from typing import List, Optional
from tool.codebase_index import _indexer

def read_related_files(file_path: str, include_imports: bool = True, include_callers: bool = True) -> str:
    """
    Read a file along with its related files (imports, callers, etc.).
    Provides full context for understanding code relationships.
    
    Args:
        file_path: Path to the main file
        include_imports: Include files that this file imports
        include_callers: Include files that import/call functions from this file
    
    Returns:
        Combined content of related files
    """
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"
    
    # Index the file first if not already indexed
    if file_path not in _indexer.functions:
        _indexer.index_file(file_path)
    
    related_files = set([file_path])
    
    if include_imports:
        deps = _indexer.get_file_dependencies(file_path)
        related_files.update(deps)
    
    if include_callers:
        # Find files that import this file
        file_name = os.path.basename(file_path).replace('.py', '')
        for other_file, imports in _indexer.imports.items():
            for imp in imports:
                if file_name in imp:
                    related_files.add(other_file)
    
    # Read all related files
    output = []
    for rel_file in sorted(related_files):
        if os.path.exists(rel_file):
            try:
                with open(rel_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                output.append(f"\n{'='*80}")
                output.append(f"FILE: {rel_file}")
                output.append(f"{'='*80}\n")
                output.append(content)
            except Exception as e:
                output.append(f"\nError reading {rel_file}: {str(e)}\n")
    
    return "\n".join(output)


def read_function_context(function_name: str, max_files: int = 5) -> str:
    """
    Read all files containing a function definition and its usages.
    
    Args:
        function_name: Name of the function
        max_files: Maximum number of files to read
    
    Returns:
        Combined content of relevant files
    """
    # Find function definitions
    definitions = _indexer.find_function(function_name)
    
    if not definitions:
        return f"Function '{function_name}' not found"
    
    # Find usages
    usages = _indexer.find_usages(function_name)
    
    files_to_read = set()
    
    # Add definition files
    for defn in definitions[:max_files]:
        files_to_read.add(defn["file"])
    
    # Add usage files
    for usage in usages[:max_files]:
        # Extract file path from usage string
        if "(" in usage:
            file_path = usage.split("(")[0].strip()
            if os.path.exists(file_path):
                files_to_read.add(file_path)
    
    # Read all files
    output = [f"Context for function: {function_name}\n"]
    for file_path in sorted(files_to_read):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                output.append(f"\n{'='*80}")
                output.append(f"FILE: {file_path}")
                output.append(f"{'='*80}\n")
                output.append(content)
            except Exception as e:
                output.append(f"\nError reading {file_path}: {str(e)}\n")
    
    return "\n".join(output)


def read_multiple_files(file_paths: List[str]) -> str:
    """
    Read multiple files together for context.
    
    Args:
        file_paths: List of file paths to read
    
    Returns:
        Combined content of all files
    """
    output = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            output.append(f"\nError: File not found: {file_path}\n")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            output.append(f"\n{'='*80}")
            output.append(f"FILE: {file_path}")
            output.append(f"{'='*80}\n")
            output.append(content)
        except Exception as e:
            output.append(f"\nError reading {file_path}: {str(e)}\n")
    
    return "\n".join(output)
