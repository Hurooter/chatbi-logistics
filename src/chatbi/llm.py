from openai import OpenAI
from langchain_openai import ChatOpenAI
from chatbi.config import DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url="https://api.deepseek.com",timeout=60)
MODEL="deepseek-flash"

chat_model=ChatOpenAI(
    model = MODEL,
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0,
    timeout=60
)


def chat(prompt:str,system:str="") -> str:
    messages=[]
    if system:
        messages.append({"role":"system","content":system})
    messages.append({"role":"user","content":prompt})
    resp=client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0
    )
    return resp.choices[0].message.content

