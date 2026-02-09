import asyncio
import json

from tool.mcp_connector import mcp_connector


class ToolManager:
  def __init__(self):
    self._tools = {}
    self._schema = []

  def register(self,*,name,description,parameters,tool): ## idhar * position ke liye 

    ## save fucntion
    self._tools[name] = tool

    ## save schema for llm

    self._schema.append({
      "type":"function",
      "function":{
        "name":name,
        "description":description,
        "parameters":parameters
      }
    })

  
  def getSchema(self):
    ## before mcp
    # return self._schema
    ## after 
    all_schemas = self._schema.copy()
    mcp_schemas = mcp_connector.get_tool_schemas()
    all_schemas.extend(mcp_schemas)

    return all_schemas

    
  
  def run(self,tool_call):
    ## this will run the tool which is called by llm and return will be in string always

    name = tool_call["function"]["name"]
    agrument = tool_call["function"].get("arguments","")
    
    try:
      args = json.loads(agrument) if agrument else {}

      if args is None:
        args = {}

    except json.decoder.JSONDecodeError:
      return "Error: invalid json argument from llm"
    
    if name in self._tools:
    
      try:
        return self._tools[name](**args)
    
      except TypeError as e:
        return f"Error: Tool arguments mismatch. {str(e)}"
      
      except Exception as e:
        return f"Error: executing tool {name} {str(e)}"
      

      ## for mcp
    else:
        # Check if MCP handles it
      result = mcp_connector.call_tool(name, args)
      if result is not None:
            return result
        
      return f"Error: Unknown tool '{name}'"
    
    ## ** used because llm give you this data {path : main.py }
    ## so direct ye pass karoge to error confirm h so ** isko main.py kar deta h simple
    
     
  
    



