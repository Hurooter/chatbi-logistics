from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from chatbi.llm import chat_model
from chatbi.nodes.sql_generator import SYSTEM_PROMPT
from chatbi.tools.agent_tools import calc_tool, schema_tool, sql_tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode


TOOLS=[schema_tool,calc_tool,sql_tool]
_agent_with_tools = chat_model.bind_tools(TOOLS)
MAX_STEPS = 8
SYSTEM_PROMPT="""你是物流仓储业务的数据分析助手，回答仓库、库存、出入库、运单相关的问题。

你手上有三个工具：
- schema_tool：查看数据库表结构
- sql_tool：执行只读 SQL 查询
- calc_tool：做算术计算

工作方式：
1. 不确定表名或字段名时，先用 schema_tool 查清楚
2. 用 sql_tool 把数据查出来
3. 要算占比、增长率时用 calc_tool，不要自己心算
4. 最后用自然语言把结论讲给用户，不要罗列原始数据

重要：调用工具时，绝对不要输出任何文字说明，直接调用工具即可；只有在给出最终结论时才输出文字。"""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]

def agent_node(state:AgentState) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {"messages":[_agent_with_tools.invoke(messages)]}

def force_answer(state:AgentState) -> dict:
    nudge = SystemMessage(content="你已连续调用工具到达上限，请立即基于现有信息用自然语言回答，不要再调用工具。")
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"] + [nudge]
    return {"messages":[chat_model.invoke(messages)]}

def rounds_this_turn(messages:list) -> int:
    """本轮提问已经执行过的工具轮数：只数最后一条 human 消息之后的 ToolMessage"""
    n = 0
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            break
        if isinstance(m, ToolMessage):
            n += 1
    return n

def should_continue(state:AgentState) -> str:
    # 有工具调用就一律先去执行，保证 tool_calls 后面一定跟着对应的工具结果
    if not state["messages"][-1].tool_calls:
        return END
    return "tools"

def after_tools(state:AgentState) -> str:
    # 工具执行完再判断是否触顶，避免留下没人回应的 tool_calls
    if rounds_this_turn(state["messages"]) >= MAX_STEPS:
        return "force_answer"
    return "agent"

def build_agent_graph(checkpointer):
    builder = StateGraph(AgentState)
    builder.add_node("agent",agent_node)
    builder.add_node("tools",ToolNode(TOOLS))
    builder.add_node("force_answer",force_answer)

    builder.add_edge(START,"agent")
    builder.add_conditional_edges("agent",should_continue,{"tools":"tools",END:END})
    builder.add_conditional_edges("tools",after_tools,{"agent":"agent","force_answer":"force_answer"})
    builder.add_edge("force_answer",END)

    return builder.compile(checkpointer=checkpointer)

graph = build_agent_graph(MemorySaver())




