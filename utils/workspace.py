"""Workspace configuration and path safety validation.

This module defines protected directories (agent's own code) and provides
path validation to prevent the AI from modifying its own codebase.
"""

import os

# Agent's own directories (PROTECTED - cannot be modified by AI)
PROTECTED_DIRS = [
    "agent",
    "tool",
    "context",
    "utils",
    "config",
    "propmts"
]

# Default workspace directory (SAFE - can be modified)
WORKSPACE_DIR = "workspace"

# Get absolute paths
AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_PATH = os.path.join(AGENT_ROOT, WORKSPACE_DIR)


def is_safe_path(path: str) -> tuple:
    """Check if a file path is safe to modify.
    
    Args:
        path: File path to validate
        
    Returns:
        tuple: (is_safe: bool, message: str)
    """
    try:
        abs_path = os.path.abspath(path)
        
        # Check if path is in protected directories
        for protected in PROTECTED_DIRS:
            protected_path = os.path.join(AGENT_ROOT, protected)
            if abs_path.startswith(protected_path):
                return False, f"🚫 Cannot modify protected directory: {protected}/"
        
        # Path is safe
        return True, "Path is safe"
    
    except Exception as e:
        return False, f"Error validating path: {str(e)}"


def ensure_workspace_exists():
    """Create workspace directory if it doesn't exist."""
    if not os.path.exists(WORKSPACE_PATH):
        os.makedirs(WORKSPACE_PATH)
        print(f"✅ Created workspace directory: {WORKSPACE_DIR}/")
