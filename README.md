# 智问 · 企业内部知识库问答 Agent 系统

基于 **LangChain + Chroma + DeepSeek + 阿里云百炼嵌入** 的 RAG 企业知识库问答系统，适合作为大模型应用开发的入门学习项目。

| 模块 | 技术 |
| --- | --- |
| 后端 | Python 3.10+、Flask、Flask-SQLAlchemy、Flask-JWT-Extended |
| RAG / Agent | LangChain 1.x（`create_agent` 工具调用）、Chroma 本地向量库 |
| 大模型 | DeepSeek `deepseek-flash`（OpenAI 兼容协议） |
| 嵌入模型 | 阿里云百炼 `qwen3.7-text-embedding-flash`（OpenAI 兼容模式） |
| 数据库 | MySQL 8（`db_enterprise_qa`，端口 3306） |
| 前端 | Vue 3、Vite、Element Plus、Pinia、Vue Router、ECharts、markdown-it |

## 一、目录结构

```
my_QA/
├─ sql/db_enterprise_qa.sql        建表语句 + 测试数据
├─ backend-server/                 Flask 后端
│  ├─ app.py                       启动入口（应用工厂）
│  ├─ config.py                    配置（读取 .env）
│  ├─ extensions.py                db / jwt / cors 扩展实例
│  ├─ models/                      ORM 模型：用户、知识库、文档、会话、消息、反馈
│  ├─ routes/                      接口蓝图：auth / user / kb / document / chat / dashboard
│  ├─ services/
│  │  ├─ llm_factory.py            创建 DeepSeek、百炼 Embedding、Chroma 客户端
│  │  ├─ rag_service.py            文档加载 → 切分 → 向量化 → 检索 → 生成
│  │  └─ agent_service.py          LangChain Agent + 工具定义
│  ├─ utils/                       统一响应、鉴权装饰器、MD5 等
│  ├─ sample_docs/                 示例制度文档（测试数据已关联）
│  ├─ uploads/                     上传文件（自动创建）
│  └─ chroma_data/                 Chroma 持久化目录（自动创建）
└─ frontend/                       Vue 3 前端
   └─ src/
      ├─ api/                      接口封装（含 SSE 流式解析）
      ├─ stores/                   Pinia 用户状态
      ├─ router/                   路由 + 角色守卫
      ├─ layouts/AdminLayout.vue   管理后台布局
      ├─ views/Login.vue           登录页
      ├─ views/admin/              数据概览、知识库、文档、问答记录、用户管理
      ├─ views/chat/ChatView.vue   ChatGPT 风格对话页
      ├─ components/               消息气泡、输入框、引用来源、统计卡片等
      └─ styles/                   设计令牌（科技蓝 + 高级灰）与全局样式
```

## 二、快速开始

### 1. 初始化数据库

```bash
mysql -uroot -p < sql/db_enterprise_qa.sql
```

### 2. 启动后端

```bash
cd backend-server
pip install -r requirements.txt
copy .env.example .env      # Linux / macOS 使用 cp
# 编辑 .env：填写 MySQL 密码、DEEPSEEK_API_KEY、DASHSCOPE_API_KEY
python app.py               # 运行在 http://127.0.0.1:5000
```

- DeepSeek API Key：<https://platform.deepseek.com>
- 百炼 API Key：<https://bailian.console.aliyun.com>

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev                 # 访问 http://localhost:5173
```

开发环境下 Vite 会把 `/api` 代理到 `http://127.0.0.1:5000`。

### 4. 体验账号

| 账号 | 密码 | 角色 |
| --- | --- | --- |
| admin | 123456 | 管理员（后台 + 问答） |
| zhangsan / lisi / wangwu | 123456 | 普通用户（仅问答） |
| zhaoliu | 123456 | 已禁用账号 |

数据库中密码以 MD5 存储（`e10adc3949ba59abbe56e057f20f883e`）。前端提交前先做 MD5，后端直接比对。

### 5. 首次使用

测试数据中的 5 篇文档指向 `backend-server/sample_docs/`，状态为 **待处理**。请用 admin 登录，进入「文档管理」，逐个点击 **向量化**，状态变为「已完成」后即可在「智能问答」中提问，例如：

- 入职满 3 年，年假有几天？
- 去上海出差住宿费报销标准是多少？
- VPN 连接不上应该怎么排查？

## 三、核心原理

```
用户提问
  │
  ▼
Flask /api/chat/stream (SSE)
  │
  ▼
LangChain Agent（DeepSeek）──判断是否需要工具──┐
  │                                            │
  │  search_knowledge(query)                   │ get_current_time()
  │    ├─ 百炼 Embedding 向量化问题            │
  │    └─ Chroma 相似度检索 Top-K 片段         │
  │                                            │
  ▼                                            │
大模型结合检索结果 + 历史对话生成回答 ◀─────────┘
  │
  ▼
逐 token 推送给前端，结束后保存消息与引用来源到 MySQL
```

- **文档入库**（`rag_service.ingest_document`）：LangChain Loader 读取 txt / md / pdf / docx，用 `RecursiveCharacterTextSplitter` 切分（默认 500 字、重叠 50 字），向量化后写入该知识库对应的 Chroma 集合，metadata 中记录 `doc_id`，方便删除和溯源。
- **两种问答模式**：`.env` 中 `AGENT_MODE=true` 时使用 Agent（由模型自主决定调用工具），设为 `false` 时使用固定的「检索 + 生成」RAG 链。两种实现可以对照学习。
- **SSE 事件**：`tool`（开始调用工具）、`tool_done`（工具完成）、`token`（增量文本）、`done`（结束，附带引用来源）、`error`（出错）。

## 四、主要接口

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | /api/auth/login | 登录 | 公开 |
| GET | /api/auth/info | 当前用户 | 登录 |
| PUT | /api/auth/password | 修改密码 | 登录 |
| GET/POST/PUT/DELETE | /api/users | 用户管理 | 管理员 |
| GET | /api/kb | 知识库列表 | 登录 |
| POST/PUT/DELETE | /api/kb | 知识库维护 | 管理员 |
| GET | /api/documents | 文档列表 | 管理员 |
| POST | /api/documents/upload | 上传并向量化 | 管理员 |
| POST | /api/documents/{id}/vectorize | 重新向量化 | 管理员 |
| DELETE | /api/documents/{id} | 删除文档及向量 | 管理员 |
| GET/POST/PUT/DELETE | /api/chat/sessions | 会话管理 | 登录 |
| GET | /api/chat/sessions/{id}/messages | 会话消息 | 登录 |
| POST | /api/chat/stream | SSE 流式问答 | 登录 |
| POST | /api/chat/messages/{id}/feedback | 点赞 / 点踩 | 登录 |
| GET | /api/chat/records | 问答记录审计 | 管理员 |
| GET | /api/dashboard/stats | 首页统计 | 管理员 |

## 五、常见问题

1. **向量化失败**：检查 `DASHSCOPE_API_KEY` 和 `EMBEDDING_MODEL` 是否正确；失败原因会显示在文档状态的提示中。
2. **问答报错「大模型调用失败」**：检查 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`。如果所用模型不支持工具调用，把 `AGENT_MODE` 设为 `false`。
3. **更换嵌入模型后检索异常**：不同模型的向量维度不同，请删除 `chroma_data/` 目录后重新向量化全部文档。
4. **MySQL 连接失败**：确认 `.env` 中的账号密码，以及 MySQL 8 服务已启动。
