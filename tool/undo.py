from agent.checkpoint import checkpoint_mgr

def undo_action():
    return checkpoint_mgr.restore_last_checkpoint()