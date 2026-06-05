"""
Pinecone vector store client — uses Cohere embeddings (free tier, 1024-dim).
Matches existing Pinecone index configured for 1024 dimensions.
"""
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore

_pc: Pinecone | None = None
_embeddings: CohereEmbeddings | None = None


def get_pinecone_client() -> Pinecone:
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return _pc


def get_embeddings() -> CohereEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = CohereEmbeddings(
            model="embed-english-v3.0",  # 1024-dim, matches Pinecone index
            cohere_api_key=os.environ["COHERE_API_KEY"],
        )
    return _embeddings


def get_or_create_index(index_name: str) -> None:
    """Create Pinecone index if it doesn't exist."""
    pc = get_pinecone_client()
    existing = [i.name for i in pc.list_indexes()]
    if index_name not in existing:
        pc.create_index(
            name=index_name,
            dimension=1024,  # Cohere embed-english-v3.0 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"Created Pinecone index: {index_name}")
    else:
        print(f"Pinecone index already exists: {index_name}")


def get_vector_store(namespace: str = "resume") -> PineconeVectorStore:
    """Return a LangChain PineconeVectorStore for the given namespace."""
    index_name = os.environ["PINECONE_INDEX_NAME"]
    return PineconeVectorStore(
        index_name=index_name,
        embedding=get_embeddings(),
        namespace=namespace,
        pinecone_api_key=os.environ["PINECONE_API_KEY"],
    )


def get_retriever(namespaces: list[str] = None, k: int = 6):
    """Search across multiple Pinecone namespaces and merge results."""
    if namespaces is None:
        namespaces = ["resume", "github"]

    retrievers = [
        get_vector_store(namespace=ns).as_retriever(
            search_kwargs={"k": max(1, k // len(namespaces))}
        )
        for ns in namespaces
    ]

    if len(retrievers) == 1:
        return retrievers[0]

    # Simple combined retriever — no external dependency needed
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from typing import List

    class MultiNamespaceRetriever(BaseRetriever):
        retrievers: list

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
        ) -> List[Document]:
            docs = []
            for r in self.retrievers:
                docs.extend(r.invoke(query))
            return docs

    return MultiNamespaceRetriever(retrievers=retrievers)

