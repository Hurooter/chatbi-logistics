import asyncio
from pathlib import Path
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from chatbi.llm import chat_model
from chatbi.mcp_tools import connect

SERVER = str(Path(__file__).resolve().parents[1] / "src" / "chatbi" / "mcp_server.py")

SYSTEM_PROMPT="""你是物流仓储业务的数据分析助手，回答仓库、库存、出入库、运单相关的问题。

你手上有三个工具：
- schema_tool：查看数据库表结构
- sql_tool：执行只读 SQL 查询
- calc_tool：做算术计算

工作方式：
1. 不确定表名或字段名时，先用 schema_tool 查清楚
2. 用 sql_tool 把数据查出来
3. 要算占比、增长率时用 calc_tool，不要自己心算
4. 最后用自然语言把结论讲给用户，不要罗列原始数据"""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_agent_graph(tools):
    model = chat_model.bind_tools(tools)
    async def agent_node(state: AgentState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [await model.ainvoke(messages)]}

    def should_continue(state: AgentState) -> str:
        return "tools" if state["messages"][-1].tool_calls else END

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=MemorySaver())


async def main():
    async with connect(SERVER) as tools:
        print("从 MCP 拿到的工具：", [t.name for t in tools])
        graph = build_agent_graph(tools)
        config = {"configurable": {"thread_id":"mcp-cli"}}
        while True:
            question = input("\n你问？")
            if question.strip() in {"exit","q","退出"}:
                break
            result = await graph.ainvoke({"messages":[("user",question)]},config)
            print("回答：", result["messages"][-1].content)

asyncio.run(main())