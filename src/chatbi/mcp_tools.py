"""把 MCP server 上的工具取下来，转成 LangChain 工具。
现实中这一步由 langchain-mcp-adapters 的 load_mcp_tools() 一行完成；
该适配器目前仍基于 mcp 1.x 的 API，与本机 mcp 2.x 不兼容，所以手写这一层。
"""
import sys
from contextlib import asynccontextmanager

from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import create_model

_TYPES = {"integer": int, "string": str, "number": float, "boolean": bool}


def _schema_to_model(name: str, schema: dict):
    fields = {}
    required = set(schema.get("required", []))
    for field_name, spec in schema.get("properties", {}).items():
        py_type = _TYPES.get(spec.get("type"), str)
        fields[field_name] = (py_type, ... if field_name in required else None)
    return create_model(f"{name}_args", **fields)


@asynccontextmanager
async def connect(server_path: str):
    """起 MCP server 子进程，把它的工具转成 LangChain 工具列表交出去用。"""
    params = StdioServerParameters(command=sys.executable, args=[server_path])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()

            def make_tool(remote_name):
                async def call(**kwargs):
                    result = await session.call_tool(remote_name, kwargs)
                    return "\n".join(getattr(c, "text", str(c)) for c in result.content)

                return call

            tools = [
                StructuredTool.from_function(
                    coroutine=make_tool(remote.name),
                    name=remote.name,
                    description=remote.description,
                    args_schema=_schema_to_model(remote.name, remote.input_schema),
                )
                for remote in listed.tools
            ]
            yield tools