"""打桩：让模型永远要求调工具，逼图进环，看防护是否收口。"""
from langchain_core.messages import AIMessage

import chatbi.agent_graph as ag

class AlwaysTool:
    def invoke(self, messages, **kwargs):
        return AIMessage(content="", tool_calls=[{"name": "schema_tool", "args": {}, "id": "x"}])

class EchoAnswer:
    def invoke(self, messages, **kwargs):
        return AIMessage(content="（收口：不再调工具，直接回答）")


ag._agent_with_tools = AlwaysTool()
ag.chat_model = EchoAnswer()

g = ag.build_agent_graph()
out = g.invoke({"messages": [("user", "hi")]},
               {"configurable": {"thread_id": "loop-guard"}, "recursion_limit": 50})

print("消息数:", len(out["messages"]))
print("序列:", [type(m).__name__ for m in out["messages"]])
print("最后一条:", out["messages"][-1].content)