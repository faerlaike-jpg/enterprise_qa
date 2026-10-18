"""
RAG（检索增强生成）核心服务
包含：文档加载 -> 文本切分 -> 向量化入库 -> 相似度检索 -> 拼接 Prompt -> 大模型生成
"""
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import BASE_DIR, Config
from services.llm_factory import get_chroma_client, get_embeddings, get_llm

# 普通 RAG 模式下的系统提示词
RAG_SYSTEM_PROMPT = """你是一名专业的企业内部知识库助手，请严格依据【参考资料】回答员工的问题。
要求：
1. 回答准确、简洁、条理清晰，可使用 Markdown 格式（列表、加粗、表格等）；
2. 如果参考资料中没有相关内容，请明确告知“知识库中暂未找到相关信息”，不要编造；
3. 不要在回答中暴露“参考资料”这几个字，直接给出结论即可。

【参考资料】
{context}
"""


class RagService:
    """RAG 服务类，封装与 Chroma 向量库及大模型的所有交互"""

    def __init__(self):
        """初始化文本切分器"""
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            # 针对中文优化的分隔符，优先按段落、句子切分
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )

    # ------------------------------------------------------------------
    # 向量库相关
    # ------------------------------------------------------------------
    def get_vectorstore(self, collection_name):
        """
        获取指定知识库对应的 Chroma 向量库对象
        :param collection_name: Chroma 集合名
        :return: langchain_chroma.Chroma 实例
        """
        return Chroma(
            client=get_chroma_client(),
            collection_name=collection_name,
            embedding_function=get_embeddings(),
        )

    def delete_collection(self, collection_name):
        """
        删除整个知识库的向量集合
        :param collection_name: Chroma 集合名
        """
        client = get_chroma_client()
        try:
            client.delete_collection(collection_name)
        except Exception:
            # 集合不存在时忽略
            pass

    def delete_document_vectors(self, collection_name, doc_id):
        """
        删除某个文档对应的所有向量片段
        :param collection_name: Chroma 集合名
        :param doc_id: 文档ID（入库时写在 metadata 中）
        """
        collection = get_chroma_client().get_or_create_collection(collection_name)
        collection.delete(where={"doc_id": doc_id})

    # ------------------------------------------------------------------
    # 文档入库
    # ------------------------------------------------------------------
    @staticmethod
    def load_file(file_path, file_type):
        """
        根据文件类型选择 LangChain 文档加载器读取内容
        :param file_path: 文件绝对路径
        :param file_type: 文件类型 txt/md/pdf/docx
        :return: LangChain Document 列表
        """
        if file_type in ("txt", "md"):
            loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
        elif file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"不支持的文件类型：{file_type}")
        return loader.load()

    def ingest_document(self, collection_name, doc_id, file_name, file_path, file_type):
        """
        将文档加载、切分并写入向量库
        :param collection_name: 知识库对应的 Chroma 集合名
        :param doc_id: 文档ID
        :param file_name: 原始文件名（用于展示引用来源）
        :param file_path: 文件路径（相对 backend-server 或绝对路径）
        :param file_type: 文件类型
        :return: 切分后的片段数量
        """
        abs_path = file_path if os.path.isabs(file_path) else os.path.join(BASE_DIR, file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")

        docs = self.load_file(abs_path, file_type)
        chunks = self.splitter.split_documents(docs)
        chunks = [c for c in chunks if c.page_content.strip()]
        if not chunks:
            raise ValueError("文档内容为空，无法向量化")

        # 为每个片段写入元数据，便于检索时溯源与按文档删除
        for idx, chunk in enumerate(chunks):
            chunk.metadata = {
                "doc_id": doc_id,
                "file_name": file_name,
                "chunk_index": idx,
                "page": chunk.metadata.get("page", 0),
            }

        # 先删除旧向量，保证重复向量化时不会产生重复数据
        self.delete_document_vectors(collection_name, doc_id)
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        self.get_vectorstore(collection_name).add_documents(chunks, ids=ids)
        return len(chunks)

    # ------------------------------------------------------------------
    # 检索与生成
    # ------------------------------------------------------------------
    def retrieve(self, collection_name, query, top_k=None):
        """
        相似度检索
        :param collection_name: Chroma 集合名
        :param query: 用户问题
        :param top_k: 返回片段数量
        :return: LangChain Document 列表
        """
        return self.get_vectorstore(collection_name).similarity_search(query, k=top_k or Config.TOP_K)

    @staticmethod
    def docs_to_context(docs):
        """
        将检索到的文档片段拼接为 Prompt 上下文
        :param docs: Document 列表
        :return: 拼接后的字符串
        """
        if not docs:
            return "（无相关资料）"
        return "\n\n".join(
            f"[{i + 1}] 来源：{d.metadata.get('file_name', '未知')}\n{d.page_content}" for i, d in enumerate(docs)
        )

    @staticmethod
    def docs_to_sources(docs):
        """
        将文档片段转换为前端展示用的引用来源列表
        :param docs: Document 列表
        :return: [{"file_name":..., "content":..., "doc_id":...}]
        """
        return [
            {
                "doc_id": d.metadata.get("doc_id"),
                "file_name": d.metadata.get("file_name", "未知"),
                "content": d.page_content[:300],
            }
            for d in docs
        ]

    @staticmethod
    def build_history(history):
        """
        将数据库中的历史消息转换为 LangChain 消息对象
        :param history: [{"role": "user"/"assistant", "content": "..."}]
        :return: HumanMessage / AIMessage 列表
        """
        messages = []
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
        return messages

    def stream_answer(self, collection_name, question, history, sources_holder):
        """
        普通 RAG 链模式：先检索，再把资料放入 Prompt 交给大模型流式生成
        :param collection_name: Chroma 集合名
        :param question: 用户问题
        :param history: 历史消息列表
        :param sources_holder: 用于回传引用来源的列表（调用方读取）
        :return: 生成器，逐个产出事件字典
        """
        yield {"type": "tool", "name": "search_knowledge"}
        docs = self.retrieve(collection_name, question)
        sources_holder.extend(self.docs_to_sources(docs))

        messages = [SystemMessage(content=RAG_SYSTEM_PROMPT.format(context=self.docs_to_context(docs)))]
        messages.extend(self.build_history(history))
        messages.append(HumanMessage(content=question))

        for chunk in get_llm().stream(messages):
            if chunk.content:
                yield {"type": "token", "content": chunk.content}


# 全局单例
rag_service = RagService()
