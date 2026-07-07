"""Retrieval-Augmented Generation (RAG) utilities and tool.

This module builds an in-memory RAG pipeline that:
- Loads PDF documents from `RAG_DATA_DIR` (default: "data").
- Splits documents into chunks using a token-aware splitter.
- Embeds chunks with OpenAI and stores vectors in an in-memory Qdrant store.
- Exposes a LangChain Tool `retrieve_information` that retrieves relevant
  context and generates a response constrained to that context.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, TypedDict

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

# Shared RAG prompt. Exposed so evaluation harnesses can reuse the exact prompt.
RAG_HUMAN_TEMPLATE = (
    "\n#CONTEXT:\n{context}\n\nQUERY:\n{query}\n\n"
    "Use the provide context to answer the provided user query. "
    "Only use the provided context to answer the query. If you do not know the answer, or it's not contained in the provided context respond with \"I don't know\""
)


def _tiktoken_len(text: str) -> int:
    """Return token length using tiktoken; used for chunk length measurement."""
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
    return len(tokens)


def build_prompt() -> ChatPromptTemplate:
    """Return the shared RAG chat prompt (expects `context` and `query`)."""
    return ChatPromptTemplate.from_messages([("human", RAG_HUMAN_TEMPLATE)])


def build_fireworks_generator(model_name: str | None = None) -> ChatOpenAI:
    """Return a ChatOpenAI generator pointed at Fireworks."""
    return ChatOpenAI(
        model=model_name
        or os.environ.get("FIREWORKS_CHAT_MODEL", "accounts/fireworks/models/gpt-oss-20b"),
        openai_api_key=os.environ["FIREWORKS_API_KEY"],
        openai_api_base=FIREWORKS_BASE_URL,
    )


def build_retriever(data_dir: str | None = None):
    """Load PDFs, chunk, embed with Fireworks, and return a Qdrant retriever.

    This is the single source of truth for the retrieval stack, reused by both
    the RAG graph and the evaluation notebook.
    """
    data_dir = data_dir or os.environ.get("RAG_DATA_DIR", "data")

    try:
        directory_loader = DirectoryLoader(
            data_dir, glob="**/*.pdf", loader_cls=PyMuPDFLoader
        )
        documents = directory_loader.load()
    except Exception:
        documents = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750, chunk_overlap=0, length_function=_tiktoken_len
    )
    chunks = text_splitter.split_documents(documents) if documents else []

    # Only send `dimensions` if FIREWORKS_EMBEDDING_DIM is set; otherwise let the
    # model return its native size. The Qwen3 embedding models differ (8B -> 4096,
    # 4B -> 2560), and you cannot request a size larger than the model's native
    # dimension, so a hardcoded value breaks whichever model doesn't match it.
    embedding_kwargs = {}
    _embedding_dim = os.environ.get("FIREWORKS_EMBEDDING_DIM")
    if _embedding_dim:
        embedding_kwargs["dimensions"] = int(_embedding_dim)

    embedding_model = OpenAIEmbeddings(
        model=os.environ.get(
            "FIREWORKS_EMBEDDING_MODEL", "accounts/fireworks/models/qwen3-embedding-8b"
        ),
        openai_api_key=os.environ["FIREWORKS_API_KEY"],
        openai_api_base=FIREWORKS_BASE_URL,
        check_embedding_ctx_length=False,
        **embedding_kwargs,
    )
    qdrant_vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        location=":memory:",
        collection_name="rag_collection",
    )
    return qdrant_vectorstore.as_retriever()


class _RAGState(TypedDict):
    """State schema for the simple two-step RAG graph: retrieve then generate."""

    question: str
    context: list[Document]
    response: str


def _build_rag_graph(data_dir: str):
    """Construct and compile a minimal RAG graph.

    Steps:
    1) Build the shared retriever (load -> chunk -> embed -> Qdrant).
    2) Build the shared prompt and Fireworks generator.
    3) Wire a two-node graph: retrieve -> generate.
    """
    retriever = build_retriever(data_dir)
    chat_prompt = build_prompt()
    generator_llm = build_fireworks_generator()

    def retrieve(state: _RAGState) -> _RAGState:
        retrieved_docs = retriever.invoke(state["question"]) if retriever else []
        return {"context": retrieved_docs}  # type: ignore

    def generate(state: _RAGState) -> _RAGState:
        generator_chain = chat_prompt | generator_llm | StrOutputParser()
        response_text = generator_chain.invoke(
            {"query": state["question"], "context": state.get("context", [])}
        )
        return {"response": response_text}  # type: ignore

    graph_builder = StateGraph(_RAGState)
    graph_builder = graph_builder.add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    return graph_builder.compile()


@lru_cache(maxsize=1)
def _get_rag_graph():
    """Return a cached compiled RAG graph built from RAG_DATA_DIR."""
    data_dir = os.environ.get("RAG_DATA_DIR", "data")
    return _build_rag_graph(data_dir)


@tool
def retrieve_information(
    query: Annotated[str, "query to ask the retrieve information tool"],
):
    """Use Retrieval Augmented Generation to retrieve information about feline health, including life stage care, nutrition, vaccinations, parasite control, behavior, diagnostics, and veterinary guidelines for cats."""
    graph = _get_rag_graph()
    result = graph.invoke({"question": query})
    # Prefer returning the response string if available
    if isinstance(result, dict) and "response" in result:
        return result["response"]
    return result
