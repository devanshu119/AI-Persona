"""
LangChain RAG chain using Groq (free LLM) — LCEL style for langchain 1.x compatibility.
"""
import os
from typing import AsyncIterator

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from rag.persona_prompt import PERSONA_SYSTEM_PROMPT
from rag.pinecone_client import get_retriever


def get_llm(streaming: bool = False) -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        streaming=streaming,
        groq_api_key=os.environ["GROQ_API_KEY"],
    )


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def get_qa_chain():
    """Build LCEL RAG chain: retrieve → format → prompt → LLM → parse."""
    llm = get_llm()
    retriever = get_retriever(namespaces=["resume", "github"], k=6)

    prompt = PromptTemplate(
        template=PERSONA_SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


async def stream_rag_response(query: str) -> AsyncIterator[str]:
    """Stream tokens from RAG chain for the chat interface (SSE)."""
    llm = get_llm(streaming=True)
    retriever = get_retriever(namespaces=["resume", "github"], k=6)

    prompt = PromptTemplate(
        template=PERSONA_SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    async for token in chain.astream(query):
        yield token


def get_rag_context_for_vapi(query: str) -> dict:
    """Non-streaming RAG query for Vapi tool-call webhook."""
    llm = get_llm()
    retriever = get_retriever(namespaces=["resume", "github"], k=6)
    prompt = PromptTemplate(
        template=PERSONA_SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    docs = retriever.invoke(query)
    context = _format_docs(docs)
    filled = PERSONA_SYSTEM_PROMPT.replace("{context}", context).replace("{question}", query)

    answer = llm.invoke(filled).content
    sources = [
        {"source": doc.metadata.get("source", "unknown"), "snippet": doc.page_content[:200]}
        for doc in docs
    ]
    return {"answer": answer, "sources": sources}
