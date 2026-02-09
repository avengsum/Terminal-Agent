import subprocess
import os
from typing import List, Dict, Optional

def git_status() -> str:
    """
    Get git status showing modified, added, and untracked files.
    Returns a formatted string with git status information.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error: Not a git repository or git error: {result.stderr}"
        
        if not result.stdout.strip():
            return "Working tree clean - no changes"
        
        return f"Git Status:\n{result.stdout}"
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except FileNotFoundError:
        return "Error: Git not installed"
    except Exception as e:
        return f"Error getting git status: {str(e)}"


def git_diff(path: Optional[str] = None) -> str:
    """
    Show git diff for a specific file or all changes.
    
    Args:
        path: Optional file path. If None, shows all changes.
    
    Returns:
        Diff output as string
    """
    try:
        cmd = ["git", "diff"]
        if path:
            cmd.append(path)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        if not result.stdout.strip():
            return "No changes to show"
        
        return result.stdout
    
    except Exception as e:
        return f"Error getting git diff: {str(e)}"


def git_add(files: List[str]) -> str:
    """
    Stage files for commit.
    
    Args:
        files: List of file paths to stage
    
    Returns:
        Success/error message
    """
    try:
        if not files:
            return "Error: No files specified"
        
        result = subprocess.run(
            ["git", "add"] + files,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error staging files: {result.stderr}"
        
        return f"Successfully staged {len(files)} file(s): {', '.join(files)}"
    
    except Exception as e:
        return f"Error staging files: {str(e)}"


def git_commit(message: str) -> str:
    """
    Commit staged changes with a message.
    
    Args:
        message: Commit message
    
    Returns:
        Success/error message
    """
    try:
        if not message:
            return "Error: Commit message required"
        
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error committing: {result.stderr}"
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        commit_hash = hash_result.stdout.strip()[:7] if hash_result.returncode == 0 else "unknown"
        
        return f"Successfully committed: {commit_hash}\nMessage: {message}"
    
    except Exception as e:
        return f"Error committing: {str(e)}"


def git_branch(name: Optional[str] = None, create: bool = False) -> str:
    """
    List branches or create/switch to a branch.
    
    Args:
        name: Branch name (optional)
        create: If True, create new branch; if False, switch to existing
    
    Returns:
        Branch information or success message
    """
    try:
        if name:
            if create:
                result = subprocess.run(
                    ["git", "checkout", "-b", name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["git", "checkout", name],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=5
                )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            action = "Created and switched to" if create else "Switched to"
            return f"{action} branch: {name}"
        
        # List branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        return f"Branches:\n{result.stdout}"
    
    except Exception as e:
        return f"Error with git branch: {str(e)}"


def git_log(limit: int = 10, file_path: Optional[str] = None) -> str:
    """
    Show git commit history.
    
    Args:
        limit: Number of commits to show
        file_path: Optional file path to show history for
    
    Returns:
        Formatted git log
    """
    try:
        cmd = ["git", "log", f"-{limit}", "--oneline", "--decorate"]
        if file_path:
            cmd.append("--")
            cmd.append(file_path)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        if not result.stdout.strip():
            return "No commits found"
        
        return result.stdout
    
    except Exception as e:
        return f"Error getting git log: {str(e)}"


def git_show(commit_hash: Optional[str] = None) -> str:
    """
    Show details of a specific commit.
    
    Args:
        commit_hash: Commit hash (defaults to HEAD)
    
    Returns:
        Commit details
    """
    try:
        cmd = ["git", "show", "--stat"]
        if commit_hash:
            cmd.append(commit_hash)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        return result.stdout
    
    except Exception as e:
        return f"Error showing commit: {str(e)}"


def git_is_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=2
        )
        return result.returncode == 0
    except:
        return False
