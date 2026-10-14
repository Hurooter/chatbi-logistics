import json
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from pydantic import BaseModel
from chatbi import admin, stats
from chatbi.agent_graph import build_agent_graph
from chatbi.auth import create_token, hash_password, verify_password
from chatbi.config import db_conn_string
from chatbi.db import execute, query
from chatbi.deps import get_current_user, rate_limit
import secrets

saver = None
graph = None
@asynccontextmanager
async def lifespan(app):
    global graph, saver
    with PyMySQLSaver.from_conn_string(db_conn_string()) as s:
        s.setup()
        saver = s
        graph = build_agent_graph(s)
        yield

app = FastAPI(lifespan=lifespan)
app.include_router(admin.router)
app.include_router(stats.router)

class Ask(BaseModel):
    question: str
    thread_id: str

class Credentials(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

def ensure_own(thread_id:str,user_id:int) -> None:
    _,rows = query(
        "SELECT 1 FROM conversations WHERE thread_id = %s AND user_id = %s",
        (thread_id, user_id),
    )
    if not rows:
        raise HTTPException(status_code=403, detail="会话不存在或不属于你")
    execute("UPDATE conversations SET updated_at = NOW() WHERE thread_id = %s", (thread_id,))

def next_conversation_title(user_id:int) -> str:
    """给这个用户的下一个会话起名：在已有的「新会话N」里取最大编号再加 1"""
    prefix = "新会话"
    _, rows = query("SELECT title FROM conversations WHERE user_id = %s", (user_id,))
    max_n = 0
    for (title,) in rows:
        if title and title.startswith(prefix) and title[len(prefix):].isdigit():
            max_n = max(max_n, int(title[len(prefix):]))
    return f"{prefix}{max_n + 1}"

@app.post("/conversations")
def create_conversation(user_id:int = Depends(get_current_user)):
    thread_id = secrets.token_hex(16)
    execute(
        "INSERT INTO conversations (thread_id, user_id, title) VALUES (%s, %s, %s)",
        (thread_id, user_id, next_conversation_title(user_id)),
    )
    return {"thread_id":thread_id}

@app.get("/conversations")
def list_conversations(user_id: int = Depends(get_current_user)):
    _, rows = query(
        "SELECT thread_id, title, created_at, updated_at FROM conversations "
        "WHERE user_id = %s ORDER BY updated_at DESC",
        (user_id,),
    )
    return [
        {"thread_id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]}
        for r in rows
    ]

@app.delete("/conversations/{thread_id}")
def delete_conversation(thread_id:str,user_id:int = Depends(get_current_user)):
    ensure_own(thread_id, user_id)
    execute(
        "DELETE FROM conversations WHERE thread_id = %s", (thread_id,)
    )
    saver.delete_thread(thread_id)
    return {"message":"已删除"}

@app.post("/auth/register")
def register(req:Credentials):
    _,rows = query("SELECT user_id FROM users WHERE username = %s",(req.username,))
    if rows:
        raise HTTPException(status_code=409,detail="Username already exists")
    execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",(req.username,hash_password(req.password)),)
    return {"message":"注册成功"}

@app.post("/auth/login")
def login(req:Credentials):
    _,rows = query(
        "SELECT user_id,password_hash FROM users WHERE username = %s",(req.username,)
    )
    if not rows or not verify_password(req.password,rows[0][1]):
        raise HTTPException(status_code=401,detail="Incorrect username or password")
    return {"token":create_token(rows[0][0])}

@app.post("/auth/password")
def change_password(req:PasswordChange,user_id:int = Depends(get_current_user)):
    _,rows = query("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
    if not rows or not verify_password(req.old_password,rows[0][0]):
        raise HTTPException(status_code=400,detail="原密码不正确")
    execute("UPDATE users SET password_hash = %s WHERE user_id = %s",
        (hash_password(req.new_password), user_id),)
    return {"message":"密码已修改"}

@app.get("/auth/me")
def me(user_id:int = Depends(get_current_user)):
    _,rows = query("SELECT username FROM users WHERE user_id = %s",(user_id,))
    if not rows:
        raise HTTPException(status_code=404,detail="User not found")
    return {"username":rows[0][0]}

@app.post("/chat")
def chat(req:Ask,user_id:int = Depends(rate_limit)):
    ensure_own(req.thread_id, user_id)
    result = graph.invoke({"messages":[("user",req.question)]},
                          {"configurable":{"thread_id":req.thread_id},"recursion_limit":50})
    return {"answer":result["messages"][-1].content}

@app.post("/chat/stream")
def chat_stream(req:Ask,user_id:int = Depends(rate_limit)):
    ensure_own(req.thread_id, user_id)
    def gen():
        last_node = None
        yield f"data: {json.dumps({'status':'正在思考…'},ensure_ascii=False)}\n\n"
        for chunk, meta in graph.stream(
            {"messages":[("user",req.question)]},
            {"configurable":{"thread_id":req.thread_id},"recursion_limit":50},
            stream_mode="messages",
        ):
            node = meta.get("langgraph_node")
            # 节点切换时，把当前进行到哪一步告诉前端
            if node != last_node:
                if node == "tools":
                    yield f"data: {json.dumps({'status':'正在查询数据…'},ensure_ascii=False)}\n\n"
                elif last_node == "tools":
                    yield f"data: {json.dumps({'status':'正在生成回答…'},ensure_ascii=False)}\n\n"
                last_node = node
            # 只转发最终回答所在节点的 token，丢掉 tools 节点的工具产物
            if node not in ("agent", "force_answer"):
                continue
            token = chunk.content
            if token:
                yield f"data: {json.dumps({'token':token},ensure_ascii=False)}\n\n"
        # 流式结束后：把本轮实际执行的 SQL 发给前端（供给「查看 SQL」用）
        state = graph.get_state({"configurable":{"thread_id":req.thread_id}})
        sqls = []
        for m in state.values.get("messages", []):
            if m.type == "human":          # 碰到新提问就清空，只保留本轮
                sqls = []
            for tc in (getattr(m, "tool_calls", None) or []):
                if tc.get("name") == "sql_tool" and tc.get("args", {}).get("sql"):
                    sqls.append(tc["args"]["sql"])
        if sqls:
            yield f"data: {json.dumps({'sqls':sqls},ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream")


@app.get("/conversations/{thread_id}/messages")
def get_messages(thread_id: str, user_id: int = Depends(get_current_user)):
    _, rows = query(
        "SELECT 1 FROM conversations WHERE thread_id = %s AND user_id = %s",
        (thread_id, user_id),
    )
    if not rows:
        raise HTTPException(status_code=403, detail="会话不存在或不属于你")
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    out = []
    for m in state.values.get("messages", []):
        if m.type not in ("human", "ai") or not m.content:
            continue
        out.append({"role": "user" if m.type == "human" else "ai", "content": m.content})
    return out
