from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage,SystemMessage
from langgraph.graph.message import add_messages
from chatbi.llm import chat_model
from chatbi.nodes.sql_generator import SYSTEM_PROMPT
from chatbi.tools.agent_tools import calc_tool, schema_tool, sql_tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

TOOLS=[schema_tool,calc_tool,sql_tool]
_agent_with_tools = chat_model.bind_tools(TOOLS)
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
    messages: Annotated[list[AnyMessage],add_messages]

def agent_node(state:AgentState) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {"messages":[_agent_with_tools.invoke(messages)]}

def should_continue(state:AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

def build_agent_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent",agent_node)
    builder.add_node("tools",ToolNode(TOOLS))

    builder.add_edge(START,"agent")
    builder.add_conditional_edges("agent",should_continue,{"tools":"tools",END:END})
    builder.add_edge("tools","agent")

    return builder.compile(checkpointer=MemorySaver())

graph = build_agent_graph()



