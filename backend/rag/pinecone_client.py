"""
Pinecone vector store client initialisation.
"""
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

_pc: Pinecone | None = None
_embeddings: OpenAIEmbeddings | None = None


def get_pinecone_client() -> Pinecone:
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return _pc


def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.environ["OPENAI_API_KEY"],
        )
    return _embeddings


def get_or_create_index(index_name: str) -> None:
    """Create Pinecone index if it doesn't exist."""
    pc = get_pinecone_client()
    existing = [i.name for i in pc.list_indexes()]
    if index_name not in existing:
        pc.create_index(
            name=index_name,
            dimension=1536,  # text-embedding-3-small dimension
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
    """
    Returns a retriever that searches across multiple namespaces.
    Merges results from resume + github namespaces for richer context.
    """
    from langchain.retrievers import MergerRetriever

    if namespaces is None:
        namespaces = ["resume", "github"]

    retrievers = []
    for ns in namespaces:
        vs = get_vector_store(namespace=ns)
        retrievers.append(vs.as_retriever(search_kwargs={"k": k // len(namespaces)}))

    if len(retrievers) == 1:
        return retrievers[0]
    return MergerRetriever(retrievers=retrievers)
