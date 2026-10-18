"""
知识库问答 Agent 服务
基于 LangChain 1.x 的 create_agent（工具调用 Agent），由大模型自主决定是否调用工具：
- search_knowledge：检索企业知识库
- get_current_time：获取当前日期时间（用于回答“今天”“本月”等时间相关问题）
"""
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from config import Config
from services.llm_factory import get_llm
from services.rag_service import rag_service

# Agent 系统提示词
AGENT_SYSTEM_PROMPT = """你是一名专业的企业内部知识库智能助手，名字叫“智问”。
工作规则：
1. 凡是涉及公司制度、流程、规范、IT 操作、报销标准等问题，必须先调用 search_knowledge 工具检索知识库，再依据检索结果回答；
2. 涉及“今天、现在、本月”等时间信息时，调用 get_current_time 工具；
3. 如果检索结果中没有相关内容，请明确告知“知识库中暂未找到相关信息”，不要编造；
4. 普通寒暄（如“你好”）可以直接回答，无需调用工具；
5. 回答使用简体中文，条理清晰，善用 Markdown（列表、加粗、表格）。
"""


class AgentService:
    """Agent 服务类：按请求动态创建绑定了指定知识库的 Agent，并以流式方式输出"""

    @staticmethod
    def build_tools(collection_name, sources_holder):
        """
        构建当前请求可用的工具列表
        工具通过闭包绑定当前知识库，并把检索到的片段写入 sources_holder
        :param collection_name: 当前知识库对应的 Chroma 集合名
        :param sources_holder: 引用来源收集列表
        :return: 工具列表
        """

        @tool
        def search_knowledge(query: str) -> str:
            """检索企业内部知识库。参数 query 为用于检索的关键问题，返回相关的制度文档片段。"""
            docs = rag_service.retrieve(collection_name, query, Config.TOP_K)
            # 去重后加入引用来源
            exists = {(s["doc_id"], s["content"]) for s in sources_holder}
            for s in rag_service.docs_to_sources(docs):
                if (s["doc_id"], s["content"]) not in exists:
                    sources_holder.append(s)
            return rag_service.docs_to_context(docs)

        @tool
        def get_current_time() -> str:
            """获取当前的日期、时间和星期。"""
            week = "一二三四五六日"[datetime.now().weekday()]
            return datetime.now().strftime(f"%Y年%m月%d日 %H:%M:%S 星期{week}")

        return [search_knowledge, get_current_time]

    def stream_answer(self, collection_name, question, history, sources_holder):
        """
        Agent 模式流式问答
        :param collection_name: Chroma 集合名
        :param question: 用户问题
        :param history: 历史消息列表
        :param sources_holder: 引用来源收集列表
        :return: 生成器，产出 {"type": "token"/"tool", ...} 事件
        """
        agent = create_agent(
            model=get_llm(),
            tools=self.build_tools(collection_name, sources_holder),
            system_prompt=AGENT_SYSTEM_PROMPT,
        )
        messages = rag_service.build_history(history) + [HumanMessage(content=question)]

        # stream_mode="messages" 会逐 token 返回 (消息块, 元数据)
        for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
            node = metadata.get("langgraph_node")
            if node == "model" and isinstance(chunk, AIMessage):
                # 大模型决定调用工具时，向前端推送工具调用状态（流式为 tool_call_chunks，非流式为 tool_calls）
                for tc in getattr(chunk, "tool_call_chunks", None) or chunk.tool_calls or []:
                    if tc.get("name"):
                        yield {"type": "tool", "name": tc["name"]}
                if chunk.content:
                    yield {"type": "token", "content": chunk.content}
            elif node == "tools" and isinstance(chunk, ToolMessage):
                yield {"type": "tool_done", "name": chunk.name}


# 全局单例
agent_service = AgentService()


def stream_chat(collection_name, question, history, sources_holder):
    """
    问答统一入口：根据配置 AGENT_MODE 选择 Agent 模式或普通 RAG 链模式
    :return: 事件生成器
    """
    if Config.AGENT_MODE:
        return agent_service.stream_answer(collection_name, question, history, sources_holder)
    return rag_service.stream_answer(collection_name, question, history, sources_holder)
