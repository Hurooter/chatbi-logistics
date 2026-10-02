from typing import Annotated,TypedDict
from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import END, START, StateGraph
from chatbi.nodes.explainer import explain
from chatbi.nodes.sql_fixer import fix_sql
from chatbi.nodes.sql_generator import generate_sql
from chatbi.tools.sql_runner import run_sql
from langgraph.checkpoint.memory import MemorySaver
MAX_RETRY = 2   # 业务规则：最多重写几次

class ChatBIState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]
    sql:str
    result:dict
    answer:str
    attempts:int

def _current_question(state:ChatBIState) -> str:
    return state["messages"][-1].content

def _history_text(state:ChatBIState) -> str:
    lines=[]
    for message in state["messages"][:-1]:
        role="用户" if message.type == "human" else "助手"
        lines.append(f"{role}:{message.content}")
    return "\n".join(lines)


def generate_node(state:ChatBIState) ->dict:
    sql=generate_sql(_current_question(state),_history_text(state))
    return {"sql":sql,"attempts":0}

def run_node(state:ChatBIState) ->dict:
    return {"result":run_sql(state["sql"])}

def fix_node(state:ChatBIState) ->dict:
    new_sql = fix_sql(_current_question(state), state["sql"], state["result"]["error"])
    return {"sql":new_sql,"attempts":state["attempts"]+1}

def explain_node(state:ChatBIState) ->dict:
    answer=explain(_current_question(state), state["sql"], state["result"])
    return {"answer":answer,"messages":[AIMessage(content=answer)]}

def route_after_run(state:ChatBIState) ->str:
    if state["result"]["ok"]:
        return "explain"
    if state["attempts"] >= MAX_RETRY:
        return "give_up"
    return "fix"


def give_up_node(state:ChatBIState) ->dict:
    answer= "抱歉，这个问题我试了几次都没查出来，可能库里没有相关数据。"
    return {"answer":answer,"messages":[AIMessage(content=answer)]}

def build_graph():
    builder = StateGraph(ChatBIState)
    builder.add_node("generate",generate_node)
    builder.add_node("run",run_node)
    builder.add_node("fix",fix_node)
    builder.add_node("explain",explain_node)
    builder.add_node("give_up",give_up_node)

    builder.add_edge(START,"generate")
    builder.add_edge("generate","run")
    builder.add_conditional_edges("run",route_after_run,{"explain":"explain","give_up":"give_up","fix":"fix"})
    builder.add_edge("fix","run")
    builder.add_edge("give_up",END)
    builder.add_edge("explain",END)

    return builder.compile(checkpointer=MemorySaver())


graph = build_graph()

