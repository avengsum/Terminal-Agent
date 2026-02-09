import asyncio
import threading
import sys
import json

# Check if mcp is installed
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ Error: 'mcp' library not found. Run: pip install mcp")
    sys.exit(1)

class MCPConnector:
    def __init__(self):
        self.session = None
        self._loop = None
        self._thread = None
        self.tools = []

    def start(self, command: str, args: list):
        """Starts the MCP Client in a background thread."""
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, args=(command, args), daemon=True)
        self._thread.start()
        
        # Wait for connection
        print("🔌 MCP: Connecting...", end="", flush=True)
        import time
        for _ in range(50): # Wait 5 seconds
            if self.session:
                print(" Connected! ✅")
                return True
            time.sleep(0.1)
        
        print(" ❌ Timeout. Server didn't respond.")
        return False

    def _run_loop(self, command, args):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._async_connect(command, args))

    async def _async_connect(self, command, args):
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )

        try:
            # Unpack the tuple into (read, write)
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self.session = session
                    
                    # Get tools immediately
                    result = await session.list_tools()
                    self.tools = result.tools
                    
                    # Keep connection open
                    await asyncio.Future()
                    
        except Exception as e:
            print(f"\n❌ MCP Async Error: {e}")

    def list_tools(self):
        if not self.session: return []
        return self.tools

    # ✅ THIS IS THE MISSING FUNCTION
    def get_tool_schemas(self):
        """
        Converts MCP tools into OpenAI Schema format.
        """
        schemas = []
        for tool in self.tools:
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema # MCP uses JSON Schema directly
                }
            })
        return schemas

    def call_tool(self, name, arguments):
        if not self.session: return "Error: Not connected."
        
        # Check if the tool actually exists in MCP
        is_mcp_tool = any(t.name == name for t in self.tools)
        if not is_mcp_tool:
            return None # Return None to signal "Not my tool"

        future = asyncio.run_coroutine_threadsafe(
            self.session.call_tool(name, arguments), 
            self._loop
        )
        try:
            result = future.result(timeout=10)
            # MCP returns a list of content, we usually want the text
            if hasattr(result, 'content') and result.content:
                # If content is text
                if hasattr(result.content[0], 'text'):
                    return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error calling MCP tool: {e}"

# Global Instance
mcp_connector = MCPConnector()