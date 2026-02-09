from mcp.server.fastmcp import FastMCP
import platform
import math

# Initialize the server
mcp = FastMCP("My Python Tools")

@mcp.tool()
def factorial(n: int) -> int:
    return math.factorial(n)

@mcp.tool()
def get_system_info() -> str:
    return f"System: {platform.system()} {platform.release()}, Processor: {platform.processor()}"

if __name__ == "__main__":
    mcp.run()