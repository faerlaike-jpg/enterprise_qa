"""
大模型与嵌入模型工厂
- 对话模型：DeepSeek（兼容 OpenAI 协议）
- 嵌入模型：阿里云百炼（OpenAI 兼容模式）
- 向量库客户端：Chroma 本地持久化
"""
from functools import lru_cache

import chromadb
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config import Config


@lru_cache(maxsize=1)
def get_llm():
    """
    创建 DeepSeek 对话模型实例（单例）
    :return: ChatOpenAI 实例，开启流式输出
    """
    return ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL,
        temperature=0.3,
        streaming=True,
        timeout=60,
        max_retries=2,
    )


@lru_cache(maxsize=1)
def get_embeddings():
    """
    创建阿里云百炼嵌入模型实例（单例）
    :return: OpenAIEmbeddings 实例
    """
    return OpenAIEmbeddings(
        model=Config.EMBEDDING_MODEL,
        api_key=Config.DASHSCOPE_API_KEY,
        base_url=Config.DASHSCOPE_BASE_URL,
        # 百炼只接受原始文本，不接受 tiktoken 编码后的 token 数组
        check_embedding_ctx_length=False,
        # 百炼单次批量请求最多 10 条文本
        chunk_size=10,
    )


@lru_cache(maxsize=1)
def get_chroma_client():
    """
    创建 Chroma 本地持久化客户端（单例，同一目录只能有一个客户端实例）
    :return: chromadb.PersistentClient
    """
    return chromadb.PersistentClient(path=Config.CHROMA_DIR)
