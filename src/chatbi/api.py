import fastapi
import json
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from chatbi.agent_graph import graph
from chatbi.db import execute, query
from chatbi.auth import create_token, decode_token, hash_password, verify_password
from fastapi.responses import StreamingResponse
app = FastAPI()

def get_current_user(authorization: str | None = Header(None)) -> int:
    token = (authorization or "").removeprefix("Bearer ").strip()
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401,detail="未登录或登录已过期")
    return user_id

class Ask(BaseModel):
    question: str
    thread_id: str = "default"

class Credentials(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

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

@app.post("/chat")
def chat(req:Ask,user_id:int = Depends(get_current_user)):
    result = graph.invoke({"messages":[("user",req.question)]},
                          {"configurable":{"thread_id":req.thread_id},"recursion_limit":50})
    return {"answer":result["messages"][-1].content}

@app.post("/chat/stream")
async def chat_stream(req:Ask,user_id:int = Depends(get_current_user)):
    async def gen():
        async for ev in graph.astream_events(
                {"messages":[("user",req.question)]},
            {"configurable":{"thread_id":req.thread_id},"recursion_limit":50},
            version="v2"
        ):
            if ev["event"] == "on_chat_model_stream":
                token = ev["data"]["chunk"].content
                if token:
                    yield f"data: {json.dumps({'token':token},ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream")
