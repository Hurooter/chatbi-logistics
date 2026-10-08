import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = r"D:\桌面\chatbi\src\chatbi\mcp_server.py"

async def main():
    params = StdioServerParameters(command=sys.executable,args=[SERVER])
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for t in tools.tools:
                print(t.name, "->", t.description)
asyncio.run(main())
