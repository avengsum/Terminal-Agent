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

{task}

"""

class ContextManager:
  def __init__(self,max_tokens=15000):
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

    if role == "assistant" and tool_calls is not None:
      message["tool_calls"] = tool_calls

    if role == "tool":
      if tool_call_id is None:
        raise ValueError("tool_call_id is required for tool messages")
      message["tool_call_id"] = tool_call_id
    
    self.history.append(message)
    self.manage_context()

  def manage_context(self):

    total = self.get_total_tokens()

    if total > self.max_tokens:
      print(f"⚠️ Context limit reached ({total}/{self.max_tokens}). Summarizing old messages...")
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
    if len(self.history) < 10:
      return
    
    ## 1 to ignore system prompt
    msgs_to_process = self.history[1:6]

    conversation_text = ""

    for m in msgs_to_process:
      role = m["role"]
      content = m.get("content","")
      if m.get("tool_calls"):
        content += " [Used Tool]"
      conversation_text += f"{role.upper()}: {content}\n"
    
    from agent.core import LLMClient

    client = LLMClient()

    prompt = f"""
        Summarize the following conversation snippet concisely. 
        Preserve key facts, file names created, and current status.
        
        CONVERSATION:
        {conversation_text}
        
        SUMMARY:
        """
    try:
      response = client.chat([
        {"role":"system","content":"You are a concise summarizer."},
        {"role":"user","content":prompt}
      ])

      new_summary_text = response["content"]

      ## remove 5 msg
      del self.history[1:6]

      summary_msg = {
                "role": "system", 
                "content": f"📝 [PREVIOUS CONVERSATION SUMMARY]: {new_summary_text}"
            }
      self.history.insert(1, summary_msg)
            
      print(f"✅ Context Pruned. New Summary: {new_summary_text[:50]}...")

    except Exception as e:
      print(f"❌ Summarization failed: {e}")
            # Fallback: Just delete the oldest one to prevent crash
      self.history.pop(1)
  
  def get_messages(self):
    return self.history



    