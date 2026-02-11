from tool import grep
from tool.edit_file import edit
from tool.execute_cmd import exe_cmd
from tool.glob import glob_files
from tool.subagent_tool import call_subagent
from tool.todo import add_todo, mark_done, update_status
from tool.tool_manager import ToolManager
from tool.list_file import list_files
from tool.read import read_file
from tool.undo import undo_action
from tool.webFetch_tool import web_fetch
from tool.webSearch_tool import webSearch
from tool.write import writeFile
from tool.git_tool import git_status, git_diff, git_add, git_commit, git_branch, git_log, git_show, git_is_repo
from tool.project_analyzer import get_project_info, detect_project_type, get_dependencies, find_entry_points
from tool.codebase_index import index_project, find_function, find_usages, get_file_dependencies, find_related_files
from tool.read_context import read_related_files, read_function_context, read_multiple_files

tool_manager = ToolManager()

# list_files
tool_manager.register(
    name="list_files",
    description="List files in a directory",
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path",
                "default": "."
            }
        }
    },
    tool=list_files
)

# read_file
tool_manager.register(
    name="read_file",
    description="Read the contents of a text file",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file"
            }
        },
        "required": ["path"]
    },
    tool=read_file
)

# write

tool_manager.register(
  name="write_file",
    description="Create or update a text file",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file"
            },
            "content": {
                "type": "string",
                "description": "Text content to write"
            },
            "mode": {
                "type": "string",
                "enum": ["overwrite", "append"],
                "description": "Write mode"
            }
        },
        "required": ["path", "content", "mode"]
    },
    tool=writeFile
)

tool_manager.register(
    name="edit_file",
    description="Edit a specific part of a file using search and replace",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file"
            },
            "search": {
                "type": "string",
                "description": "Text to search for"
            },
            "replace": {
                "type": "string",
                "description": "Replacement text"
            }
        },
        "required": ["path", "search", "replace"]
    },
    tool=edit
)

tool_manager.register(
    name="execute_command",
    description="Execute a terminal command (like 'python file.py'). captures output and errors.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to run in the terminal"
            }
        },
        "required": ["command"]
    },
    tool=exe_cmd
)

tool_manager.register(
    name="glob",
    description="Find files using a pattern (like *.py or **/*.md)",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern to search files"
            }
        },
        "required": ["pattern"]
    },
    tool=glob_files
)

tool_manager.register(
    name="grep",
    description="Search text inside a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path"
            },
            "text": {
                "type": "string",
                "description": "Text to search"
            }
        },
        "required": ["path", "text"]
    },
    tool=grep.grep
)

tool_manager.register(
    name="webSearch",
    description="Search the web for up-to-date information",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"]
    },
    tool=webSearch
)

tool_manager.register(
    name="web_fetch",
    description="Visit a specific URL and read its content to answer a question. Use this when the user provides a link OR when you find a link via search that you need to analyze.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the page to read (must start with http/https)"
            },
            "question": {
                "type": "string",
                "description": "The specific information you want to find on the page (e.g. 'What is the main summary?' or 'Find the installation command')"
            }
        },
        "required": ["url", "question"]
    },
    tool=web_fetch
)

tool_manager.register(
    name="add_todo",
    description="Add a task to the project plan. ALWAYS do this first.",
    parameters={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Description of the task"},
            "dependencies": {"type": "string", "description": "IDs of tasks that must finish first (e.g. '1,3')"}
        },
        "required": ["task"]
    },
    tool=add_todo
)

tool_manager.register(
    name="update_todo",
    description="Update task status to IN_PROGRESS or FAILED.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {"type": "integer"},
            "status": {"type": "string", "enum": ["PENDING", "IN_PROGRESS", "FAILED"]},
            "notes": {"type": "string", "description": "Reason for status change"}
        },
        "required": ["task_id", "status"]
    },
    tool=update_status
)

tool_manager.register(
    name="mark_done",
    description="Mark a task as COMPLETED. Requires verification proof.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {"type": "integer"},
            "verification": {"type": "string", "description": "Output or proof that the task is done"}
        },
        "required": ["task_id", "verification"]
    },
    tool=mark_done
)

tool_manager.register(
    name="call_subagent",
    description="Delegate a complex sub-task to a specialized agent. Use 'researcher' for gathering info, 'coder' for writing/testing code.",
    parameters={
        "type": "object",
        "properties": {
            "agent_type": { 
                "type": "string",
                "enum": ["coder", "researcher"],
                "description": "The type of specialist to spawn."
            },
            "task_description": {
                "type": "string",
                "description": "Specific instructions for the sub-agent."
            }
        },
        "required": ["agent_type", "task_description"]
    },
    tool=call_subagent
)

# Git Tools
tool_manager.register(
    name="git_status",
    description="Get git status showing modified, added, and untracked files.",
    parameters={
        "type": "object",
        "properties": {}
    },
    tool=git_status
)

tool_manager.register(
    name="git_diff",
    description="Show git diff for a specific file or all changes.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional file path. If not provided, shows all changes."
            }
        }
    },
    tool=git_diff
)

tool_manager.register(
    name="git_add",
    description="Stage files for commit.",
    parameters={
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to stage"
            }
        },
        "required": ["files"]
    },
    tool=git_add
)

tool_manager.register(
    name="git_commit",
    description="Commit staged changes with a message.",
    parameters={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Commit message"
            }
        },
        "required": ["message"]
    },
    tool=git_commit
)

tool_manager.register(
    name="git_branch",
    description="List branches or create/switch to a branch.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Branch name (optional - if not provided, lists branches)"
            },
            "create": {
                "type": "boolean",
                "description": "If true, create new branch; if false, switch to existing"
            }
        }
    },
    tool=git_branch
)

tool_manager.register(
    name="git_log",
    description="Show git commit history.",
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Number of commits to show",
                "default": 10
            },
            "file_path": {
                "type": "string",
                "description": "Optional file path to show history for"
            }
        }
    },
    tool=git_log
)

# Project Analysis Tools
tool_manager.register(
    name="get_project_info",
    description="Get comprehensive project information including type, structure, dependencies, and entry points.",
    parameters={
        "type": "object",
        "properties": {}
    },
    tool=get_project_info
)

tool_manager.register(
    name="detect_project_type",
    description="Detect the type of project (python, javascript, typescript, etc.) based on config files.",
    parameters={
        "type": "object",
        "properties": {}
    },
    tool=detect_project_type
)

tool_manager.register(
    name="get_dependencies",
    description="Get project dependencies from requirements.txt, package.json, etc.",
    parameters={
        "type": "object",
        "properties": {}
    },
    tool=get_dependencies
)

# Codebase Indexing Tools
tool_manager.register(
    name="index_project",
    description="Index the entire codebase to understand structure, functions, classes, and relationships. Run this first to enable code intelligence features.",
    parameters={
        "type": "object",
        "properties": {
            "root_dir": {
                "type": "string",
                "description": "Root directory to index (defaults to current directory)"
            }
        }
    },
    tool=index_project
)

tool_manager.register(
    name="find_function",
    description="Find all definitions of a function in the codebase.",
    parameters={
        "type": "object",
        "properties": {
            "function_name": {
                "type": "string",
                "description": "Name of the function to find"
            }
        },
        "required": ["function_name"]
    },
    tool=find_function
)

tool_manager.register(
    name="find_usages",
    description="Find where a function or class is used in the codebase.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of function or class to find usages for"
            }
        },
        "required": ["name"]
    },
    tool=find_usages
)

tool_manager.register(
    name="get_file_dependencies",
    description="Get files that a file imports (local dependencies).",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file"
            }
        },
        "required": ["file_path"]
    },
    tool=get_file_dependencies
)

tool_manager.register(
    name="find_related_files",
    description="Find files related to the given file (imports, callers, etc.).",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file"
            }
        },
        "required": ["file_path"]
    },
    tool=find_related_files
)

# Context Reading Tools
tool_manager.register(
    name="read_related_files",
    description="Read a file along with its related files (imports, callers) to get full context. Use this before making edits to understand code relationships.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the main file"
            },
            "include_imports": {
                "type": "boolean",
                "description": "Include files that this file imports",
                "default": True
            },
            "include_callers": {
                "type": "boolean",
                "description": "Include files that import/call functions from this file",
                "default": True
            }
        },
        "required": ["file_path"]
    },
    tool=read_related_files
)

tool_manager.register(
    name="read_function_context",
    description="Read all files containing a function definition and its usages. Provides complete context for understanding a function.",
    parameters={
        "type": "object",
        "properties": {
            "function_name": {
                "type": "string",
                "description": "Name of the function"
            },
            "max_files": {
                "type": "integer",
                "description": "Maximum number of files to read",
                "default": 5
            }
        },
        "required": ["function_name"]
    },
    tool=read_function_context
)

tool_manager.register(
    name="read_multiple_files",
    description="Read multiple files together for context. Useful when you need to understand relationships between files.",
    parameters={
        "type": "object",
        "properties": {
            "file_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to read"
            }
        },
        "required": ["file_paths"]
    },
    tool=read_multiple_files
)

tool_manager.register(
    name="undo_last_action",
    description="Revert the last file change. Use this if you broke the code and want to go back.",
    parameters={
        "type": "object",
        "properties": {}, # No arguments needed
        "required": []
    },
    tool=undo_action
)

