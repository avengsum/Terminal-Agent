import os
import shutil
import json
import time
from datetime import datetime

BACKUP_DIR = ".agent_backups"
MANIFEST_FILE = os.path.join(BACKUP_DIR, "manifest.json")

class CheckpointManager:
    def __init__(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        self.history = self._load_manifest()

    def _load_manifest(self):
        if os.path.exists(MANIFEST_FILE):
            try:
                with open(MANIFEST_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_manifest(self):
        with open(MANIFEST_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)

    def create_checkpoint(self, file_path: str, action_desc: str):
        if not os.path.exists(file_path):
            return 

        timestamp = int(time.time())
        checkpoint_id = f"ckpt_{timestamp}"
        
        ckpt_folder = os.path.join(BACKUP_DIR, checkpoint_id)
        os.makedirs(ckpt_folder, exist_ok=True)

        filename = os.path.basename(file_path)
        dest_path = os.path.join(ckpt_folder, filename)
        shutil.copy2(file_path, dest_path)

        entry = {
            "id": checkpoint_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action_desc,
            "original_file": file_path,
            "backup_location": dest_path
        }
        self.history.append(entry)
        self._save_manifest()
        
        return checkpoint_id

    def restore_last_checkpoint(self):
        if not self.history:
            return "No checkpoints found."

        last_entry = self.history.pop() 
        self._save_manifest()

        original_path = last_entry["original_file"]
        backup_path = last_entry["backup_location"]

        try:
           
            shutil.copy2(backup_path, original_path)
            return f"✅ Rolled back: {original_path} restored to state before '{last_entry['action']}'"
        except Exception as e:
            return f"❌ Rollback failed: {e}"
            
    def list_checkpoints(self):
        if not self.history: return "No history."
        return "\n".join([f"{entry['id']} - {entry['action']} ({entry['timestamp']})" for entry in self.history[-5:]])


checkpoint_mgr = CheckpointManager()