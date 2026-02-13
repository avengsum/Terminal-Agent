import os
from agent.task_manager import TaskManager
import tiktoken
import datetime

now = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")

task = TaskManager()

SYSTEM_PROMPT = f"""
You are an expert AI Software Engineer. Your goal is to help the user build, debug, and maintain high-quality code.

### OPERATING PRINCIPLES
1. **Think Before Acting:** Before writing code or calling a tool, explain your reasoning. Use a "Thought" process to analyze the request.
2. **Be Concise:** Avoid conversational filler like "Sure" or "I can help with that." Get straight to the technical solution.
3. **Accuracy First:** If you are unsure about a file path or a library version, use a tool to check it first. Do not hallucinate file contents.
4. **Security:** Never execute destructive commands (like `rm -rf /`) and always ask for confirmation before making major architectural changes.

### WORKFLOW
- **Step 1:** Analyze the user's request and the current project context.
- **Step 2:** List the files you need to read or the actions you need to take.
- **Step 3:** Perform the actions using the available tools.
- **Step 4:** Verify the result and report back to the user with the changes made.

### FORMATTING
- Provide code snippets in Markdown code blocks with the correct language tag.
- If you are suggesting a file change, show the specific lines to be changed or provide the full updated file.
- Use a clear, professional tone.

- NEVER simulate or pretend to run terminal commands. If you need to see files, you MUST use the list_files tool. Do not write the command as text; trigger the function."

Current Working Directory: {os.getcwd()}
Current Date and Time: {now}
INSTRUCTIONS:
1. The date provided above is ACCURATE. Do NOT search the internet to check the current date.
2. If the user asks "what day is it", simply reply using the SYSTEM INFORMATION above.
3. Only use Web Search for external knowledge, documentation, or events.
4. DO NOT use 'python -c' one-liners. They fail due to quoting errors.
5. ALWAYS use 'write_file' to create a python script, then run it with 'python script.py'.
6. When reading a website, use 'web_fetch'.
7. You MUST follow the Project Plan below.
8. If the plan is empty, use 'add_todo' to define steps.
9. Before running code, mark the task as IN_PROGRESS.
10. After success, mark the task as COMPLETED with verification.

### WORKSPACE ISOLATION (CRITICAL):
11. **ALWAYS create new projects in the 'workspace/' directory**
12. **NEVER modify files in: agent/, tool/, context/, utils/, config/, propmts/**
13. These directories contain YOUR OWN CODE - modifying them will BREAK YOU!
14. If user asks to modify agent code, politely explain the safety restriction.

### CODE INTELLIGENCE WORKFLOW (Claude Code Level):
11. **Before editing code:**
    - Use 'get_project_info' to understand project structure
    - Use 'index_project' to build codebase index (if not done)
    - Use 'read_related_files' to get full context before editing
    - Use 'find_function' or 'find_usages' to understand code relationships
    - Check 'git_status' to see what's changed

12. **When making changes:**
    - Read related files first to understand dependencies
    - Make changes across multiple files if needed
    - Check 'git_diff' to review changes before committing
    - Use 'git_add' and 'git_commit' with meaningful messages

13. **For complex refactoring:**
    - Use 'find_usages' to find all places a function is used
    - Use 'read_function_context' to get complete function context
    - Update all related files together
    - Verify changes work before committing

14. **Project understanding:**
    - Use 'detect_project_type' to understand project structure
    - Use 'get_dependencies' to see what packages are used
    - Use 'find_entry_points' to find main files

{task}

"""

class ContextManager:
  def __init__(self,max_tokens=10000):
    self.max_tokens = max_tokens
    self.model = "mistralai/devstral-2512:free"
    self.system_prompt = SYSTEM_PROMPT
    self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    self.encoding = tiktoken.get_encoding("cl100k_base")

  
  def count_tokens(self,text):
    if not text:
      return 0
    
    if self.encoding:
      return len(self.encoding.encode(text))
    
    return len(text)
  
  def get_total_tokens(self):
    return sum(self.count_tokens(m.get("content", "")) for m in self.history)
  
  def add_message(self,role,content,tool_calls=None,tool_call_id=None):

    if content is None:
      content = ""

    message = {
      "role":role,
      "content":content
    }

    if tool_calls: message["tool_calls"] = tool_calls
    if tool_call_id: message["tool_call_id"] = tool_call_id

    # 1. Handle System Prompt (Always at Index 0)
    if role == "system":
      if self.history and self.history[0]["role"] == "system":
          self.history[0] = message
      else:
        self.history.insert(0, message)
    else:
        self.history.append(message)

        # 2. Aggressively Prune Old Messages
    self.manage_context()

  def manage_context(self):

    total = self.get_total_tokens()

    while total > self.max_tokens and len(self.history) > 5:
      print(f"⚠️ Context limit reached ({self.get_total_tokens()}/{self.max_tokens}). Summarizing oldest messages...")
      self.summarize()

    ## before summerize

    # total_tokens = 0 

    # for message in self.history:
    #   text = message['content']
    #   token = self.count_tokens(text)
    #   # print(f"Message: {text} -> Tokens: {token}")
    #   total_tokens+=token
    #   # print(f"totaltoken: {total_tokens}")

    # while total_tokens > self.max_tokens and len(self.history) > 2:
    #   removed = self.history.pop(1)
    #   total_tokens -= self.count_tokens(removed['content'])
    #   print(f"DEBUG: Context Manager pruned an old message to save space.")

  def summarize(self):
    msg_to_summerize = 6 
    if len(self.history) < msg_to_summerize:
      return
    
    ## 1 to ignore system prompt
    msgs_to_process = self.history[1:msg_to_summerize+1]

    conversation_text = ""

    for m in msgs_to_process:
      role = m["role"]
      content = m.get("content","")
      if m.get("tool_calls"):
        content += " [Used Tool]"
      conversation_text += f"{role.upper()}: {content}\n"
    
    from agent.core import LLMClient

    client = LLMClient(api_key=os.getenv("GOOGLE"),model="gemini-2.5-pro",base_url="https://generativelanguage.googleapis.com/v1beta")

    prompt = f"""
        Summarize the following conversation snippet into ONE short paragraph (max 150 words).
    Focus ONLY on:
    1. Technical tasks completed.
    2. Files created/modified.
    3. The current goal.
    
    CONVERSATION:
    {conversation_text}
        """
    try:
      response = client.chat([
        {"role":"system","content":"You are a concise summarizer."},
        {"role":"user","content":prompt}
      ])

      new_summary = response.get("content", "Summary failed") if isinstance(response, dict) else response.content
        
        # Delete the messages we summarized
      del self.history[1:msg_to_summerize + 1]
        
        # Insert the tiny summary
      summary_msg = {"role": "user", "content": f"📝 [OLD HISTORY]: {new_summary}"}
      self.history.insert(1, summary_msg)
        
      print(f"✅ Context Pruned. New total: {self.get_total_tokens()}")

    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        self.history.pop(1) # Emergency pop to prevent infinite loop
  
  def get_messages(self):
        return self.history





    