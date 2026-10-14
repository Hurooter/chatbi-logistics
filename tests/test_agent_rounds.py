"""测 agent 图的轮次逻辑——就是之前「聊着聊着不回答」那个 bug 的修复点。"""
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END

import chatbi.agent_graph as ag
from chatbi.agent_graph import after_tools, rounds_this_turn, should_continue


def ai(with_tool: bool) -> AIMessage:
    tcs = [{"name": "sql_tool", "args": {"sql": "SELECT 1"}, "id": "c1"}] if with_tool else []
    return AIMessage(content="", tool_calls=tcs)


def tool_msg() -> ToolMessage:
    return ToolMessage(content="ok", tool_call_id="c1")


def test_rounds_only_counts_current_turn():
    msgs = [
        HumanMessage("第一问"), ai(True), tool_msg(), ai(True), tool_msg(),
        HumanMessage("第二问"), ai(True), tool_msg(),
    ]
    assert rounds_this_turn(msgs) == 1        # 只数最后一问之后的


def test_should_continue():
    assert should_continue({"messages": [ai(False)]}) == END
    assert should_continue({"messages": [ai(True)]}) == "tools"


def test_after_tools_caps(monkeypatch):
    monkeypatch.setattr(ag, "MAX_STEPS", 2)
    hit_cap = {"messages": [HumanMessage("q"), ai(True), tool_msg(), ai(True), tool_msg()]}
    below = {"messages": [HumanMessage("q"), ai(True), tool_msg()]}
    assert after_tools(hit_cap) == "force_answer"
    assert after_tools(below) == "agent"
