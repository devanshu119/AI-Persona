"""
LangChain RAG chain for the persona chatbot.
Combines resume + GitHub context to answer questions grounded in real data.
"""
import os
from typing import AsyncIterator

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from rag.persona_prompt import PERSONA_SYSTEM_PROMPT
from rag.pinecone_client import get_retriever


def get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        streaming=streaming,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )


def get_qa_chain() -> RetrievalQA:
    """Build a RAG chain with multi-namespace retrieval."""
    llm = get_llm(streaming=False)
    retriever = get_retriever(namespaces=["resume", "github"], k=6)

    prompt = PromptTemplate(
        template=PERSONA_SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return chain


async def stream_rag_response(query: str) -> AsyncIterator[str]:
    """
    Stream tokens from the RAG chain for chat interface.
    Uses streaming LLM but retrieves context first.
    """
    from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
    from langchain.schema import HumanMessage

    handler = AsyncIteratorCallbackHandler()
    streaming_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        streaming=True,
        callbacks=[handler],
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )

    # Retrieve context
    retriever = get_retriever(namespaces=["resume", "github"], k=6)
    docs = await retriever.aget_relevant_documents(query)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Build prompt
    filled_prompt = PERSONA_SYSTEM_PROMPT.replace("{context}", context).replace(
        "{question}", query
    )

    import asyncio

    async def _run():
        await streaming_llm.agenerate([[HumanMessage(content=filled_prompt)]])
        handler.done.set()

    asyncio.ensure_future(_run())

    async for token in handler.aiter():
        yield token


def get_rag_context_for_vapi(query: str) -> dict:
    """
    Non-streaming RAG query used by Vapi tool call webhook.
    Returns answer + source snippets.
    """
    chain = get_qa_chain()
    result = chain.invoke({"query": query})
    sources = [
        {"source": doc.metadata.get("source", "unknown"), "snippet": doc.page_content[:200]}
        for doc in result.get("source_documents", [])
    ]
    return {
        "answer": result["result"],
        "sources": sources,
    }
