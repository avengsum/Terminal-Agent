import os
from utils.workspace import is_safe_path
from agent.checkpoint import checkpoint_mgr

max_content_size = 200 * 1024

avl_mode = ("overwrite","append")

allowed_ext = (".txt", ".md", ".py", ".json", ".yaml", ".yml", ".js", ".java", 
               ".html", ".htm", ".css", ".jsx", ".tsx", ".ts", ".sql", ".sh",
               ".env", ".gitignore", ".dockerignore", ".editorconfig") 

allowed_files = (
        "Dockerfile", "Makefile", "Procfile", ".gitignore", 
        ".dockerignore", ".editorconfig", ".eslintrc", ".prettierrc"
    )

def writeFile(path:str,content:str,mode:str) -> str:

  _, ext = os.path.splitext(path)
  filename = os.path.basename(path)

  try:
      ## workspace safety check
    is_safe, safety_message = is_safe_path(path)
    if not is_safe:
      return f"Error: {safety_message}"
    
    # checkpoint created
    if os.path.exists(path):
        checkpoint_mgr.create_checkpoint(path, f"Modified {path} via write_file")
        print(f"🛡️  Checkpoint created for {path}")
      
      ## basic access control

    if not path or ".." in path:
      return "Error: Invalid path"
    if ext not in allowed_ext and filename not in allowed_files:
        return f"Error: file type not supported (extension: {ext or 'none'})"
  
    if not content:
      return "Error: not content provided"
  
    if len(content.encode("utf-8")) > max_content_size:
      return "Error: content size is too large"
  
    if not path.lower().endswith(allowed_ext):
      return "Error: file type not supported"
   
    if mode not in avl_mode:
      return "Error: Invalid mode"
  
  ## files rules
  
    fileExists = os.path.exists(path)

    if fileExists and mode == "overwrite":
      write_mode = "w"
    elif fileExists and mode == "append":
      write_mode = "a"
    elif not fileExists and mode ==    "append":
      return "Errror cannot append because file does not exists" 
    else:
      write_mode = "w"
  
  # write function

    parent_dict = os.path.dirname(path)

    if parent_dict and not os.path.exists(parent_dict):
      try:
        os.makedirs(parent_dict)
      
      except Exception as e:
        return f"Error creating directory: {str(e)}"


    with open(path,write_mode,encoding="utf-8",errors="replace") as f:
      f.write(content)
  
    return f"done: file {path} written mode: {mode}"
  
  except PermissionError:
    return "Error permission denied"
  
  except Exception as e:
    return f"Error writing file: {str(e)}"
  
  
