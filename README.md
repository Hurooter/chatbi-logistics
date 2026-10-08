# 物流仓储数据分析助手（ChatBI）

用自然语言查询业务数据库：**你问一句话，系统自动生成 SQL、查询数据、并把结果用自然语言讲给你听。**

面向物流仓储履约运营场景，业务覆盖仓库、商品、库存、入库单、出库单、运单。

## 效果示例

> **问**：各仓库的库存总量分别是多少
>
> **答**：8 个仓库的库存总量大多在 10 万件上下：华东仓最多，为 109,620 件；华东二仓最少，96,167 件，整体分布比较均衡。
>
> **生成的 SQL**：
> ```sql
> SELECT w.warehouse_name, SUM(i.stock_qty) AS total_stock
> FROM inventory i
> JOIN warehouses w ON i.warehouse_id = w.warehouse_id
> GROUP BY w.warehouse_id, w.warehouse_name
> ```

支持**多轮追问**：

> **问**：那华东仓的库存占八仓总量的百分之多少？
>
> **答**：华东仓库存 109,620 件，占八仓总库存的 13.37%，约为总量的七分之一。

## 技术栈

Python · LangGraph · LangChain · DeepSeek API · MySQL · MCP · uv

## 核心设计

### 1. 工具三件套

| 工具 | 作用 |
|---|---|
| `schema_tool` | 查表结构，喂给模型让它知道表名与字段名 |
| `sql_tool` | 执行只读 SQL：只放行 SELECT、结果超限自动截断、异常转文本返回 |
| `calc_tool` | 代码算数：正则白名单 + 空 builtins 双重防护 |

### 2. Agent 自主决策

模型手里拿着这包工具，**自己决定**调哪个、调几次，而不是走写死的流水线：

```
START → agent ─┬─ 需要工具 → tools ─┐
               │                     │
               └─ 可以回答 → END ←───┘   （工具跑完回到 agent）
```

实际表现：

- 问「你好」→ 不调任何工具，直接回话
- 问「库里有哪些表」→ 调 `schema_tool`
- 问「各仓库库存总量」→ 调 `sql_tool`（必要时先调 schema 确认字段）

### 3. SQL 错误自纠

SQL 执行失败时，条件边把**报错信息**路由回修复节点，由模型带着报错重写、重试；重试上限由 state 计数控制，不依赖框架默认值。

### 4. 多轮对话

基于 LangGraph checkpoint + `thread_id` 持久化会话状态，支持依赖上文的追问。

### 5. MCP 对照版

同一套数据库工具，另做了一条 **MCP（Model Context Protocol）** 路径，与「直接注册成 LangGraph 工具」对照：

| | 直接注册（`agent_graph.py`） | MCP 版（`try_agent_mcp.py`） |
|---|---|---|
| 工具住哪 | 同一个进程 | 独立子进程 |
| 怎么调用 | 普通函数调用 | stdio 协议 |
| 同步/异步 | 同步 | 异步 |
| 复用范围 | 仅本项目 | 任何 MCP 客户端 |

- `src/chatbi/mcp_server.py` —— 用 `MCPServer` 把三个工具暴露成一个独立进程
- `src/chatbi/mcp_tools.py` —— 客户端侧：起子进程、拉工具清单、把 MCP 的 `input_schema` 翻译成 LangChain 的 `args_schema`（官方适配器 `langchain-mcp-adapters` 目前仍基于 mcp 1.x API，与本机 mcp 2.x 不兼容，故手写这一层）
- `scripts/try_agent_mcp.py` —— 异步版 Agent 图，工具在运行时从 MCP 拉取

价值：**进程隔离**（server 崩了不拖垮主程序）、**跨语言**、一份 server 可同时供多个客户端使用。

### 6. 安全防护

- **SQL 白名单**：不靠关键词黑名单（会误杀 `WHERE product_name='drop table'`、又会漏杀 `SELECT ... INTO OUTFILE`），改用 `sqlglot` 把 SQL 解析成语法树——**只放行根节点为 `SELECT` 的单条语句**；解析失败一律拒绝（fail-closed）
- **查询超时**：连接设 `read_timeout`，`SELECT SLEEP(300)` 这类慢查询 10 秒内被掐断，不会拖死服务
- **结果脱敏**：在工具层对敏感列（`manager` / `customer`）打码，结果流向模型 / 日志 / 前端之前先过滤
- **死循环防护**：Agent 图三层——步数上限（`MAX_STEPS`，数已执行的工具轮数）+ 软着陆（超限转「收口节点」，缴械后直接回答）+ `recursion_limit` 框架保险丝

## 项目结构

```
chatbi/
├── sql/01_schema.sql          # 建表脚本（含反序 DROP，可重复执行）
├── scripts/
│   ├── gen_data.py            # 造数脚本（近 7 万条模拟数据）
│   ├── show_schema.py         # 打印库表结构
│   ├── try_agent.py           # Agent 版试跑入口
│   ├── try_agent_mcp.py       # MCP 版试跑入口（异步）
│   └── try_multi_turn.py      # 多轮对话验证
└── src/chatbi/
    ├── config.py              # 配置集中管理（.env）
    ├── db.py                  # MySQL 连接与查询
    ├── llm.py                 # 模型客户端
    ├── agent_graph.py         # ★ Agent 图（模型自主选工具）
    ├── graph.py               # 早期流水线图（保留对照）
    ├── mcp_server.py          # MCP server：把工具暴露成独立进程
    ├── mcp_tools.py           # MCP client：拉工具并转成 LangChain 工具
    ├── nodes/                 # SQL 生成 / 修复 / 结果解读
    └── tools/                 # 工具三件套及其 LangChain 封装
```

## 快速开始

**前置**：本地 MySQL、Python 3.14、[uv](https://docs.astral.sh/uv/)、一个 DeepSeek API Key。

### 1. 建库建表

```bash
mysql -uroot -p -e "CREATE DATABASE chatbi_logistics DEFAULT CHARACTER SET utf8mb4;"
mysql -uroot -p --default-character-set=utf8mb4 chatbi_logistics < sql/01_schema.sql
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入自己的值：

```
DEEPSEEK_API_KEY=sk-你的key
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=chatbi_logistics
```

### 3. 装依赖 + 灌数据

```bash
uv sync
uv run python scripts/gen_data.py
```

### 4. 跑起来

```bash
uv run python scripts/try_agent.py       # Agent 版（工具在同一进程）
uv run python scripts/try_agent_mcp.py   # MCP 版（工具在独立进程）
```

## 开发进度

- [x] 数据层：6 张关联业务表 + 造数脚本
- [x] 工具三件套（查表结构 / 执行只读 SQL / 代码算数）
- [x] LangGraph 图编排 + SQL 错误自纠循环
- [x] Agent 自主选择工具 + 多轮对话
- [x] MCP 对照版
- [x] 安全防护：SQL 真解析白名单 / 查询超时 / 结果脱敏 / Agent 死循环防护
- [ ] FastAPI + SSE 接口与前端页面（含鉴权、限流）
- [ ] 20 题评估集与压测报告
- [ ] Docker 打包
