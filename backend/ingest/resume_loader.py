"""
Resume loader: reads PDF, chunks it, and upserts into Pinecone 'resume' namespace.
"""
import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pinecone_client import get_vector_store, get_or_create_index


RESUME_TEXT = """
DEVANSHU VERMA
Pre-final year CSE student at IIIT Una specialising in LLM systems, RAG pipelines, and MLOps.
Shipped a production VSCode coding assistant to 3 enterprise clients; fine-tuned proprietary LLMs
and reduced retrieval hallucination by ~25%. Strong CP background (500+ DSA problems, LeetCode & Codeforces).
Seeking high-impact ML/AI roles to drive model quality and developer tooling at scale.

SKILLS
Languages: Python, SQL, C, C++, JavaScript
ML/DL: TensorFlow, Keras, PyTorch, Scikit-learn, Pandas, NumPy, OpenCV, Librosa, Matplotlib
LLM & RAG: LangChain, LLM APIs (OpenAI-compatible), Ollama, Embedding Generation, Vector Stores, Prompt Engineering
Backend/Tools: FastAPI, BeautifulSoup, Streamlit, Git, Docker (familiar), Jupyter, VS Code
MLOps & Cloud: CI/CD Pipelines, GitHub Actions, Model Fine-tuning, Hyperparameter Tuning, AWS (familiar)
Competitive Programming: 500+ DSA problems on LeetCode & Codeforces; Codeforces rating 1300+ (Pupil)

EXPERIENCE
Machine Learning Intern — Planto.ai | Feb 2025 – Jun 2025 (5 months, Remote)
Tech Stack: Next.js, Node.js, LangChain, Ollama, RAG, CI/CD
• Built a VSCode coding assistant using LLM APIs (code completion, context-aware suggestions, inline docs).
  Deployed to 3 enterprise clients, cutting developer context-switching by ~30%.
• Designed CI/CD pipelines for LLM model integration, reducing deployment time by ~40% and maintaining
  reproducible builds across staging and production environments.
• Fine-tuned Planto's proprietary LLM on 500+ curated instruction-response pairs, improving task accuracy
  by 15% over the base model on domain-specific benchmarks.
• Built RAG preprocessing workflows (chunking, embedding generation, vector store indexing), reducing
  retrieval hallucination by ~25% on enterprise codebase queries.
• Gathered requirements from 5+ enterprise partners and produced ML feature specs and Cloud integration
  roadmaps with defined acceptance criteria.

PROJECTS
Oil Spill Detection using Computer Vision | Feb 2025 – Mar 2025
Tech Stack: Python, PyTorch, OpenCV, Streamlit
• Trained U-Net, DeepLabv3, and CNN models on SAR satellite datasets, achieving >90% IoU.
• Deployed via Streamlit with real-time segmentation mask overlay on uploaded images.
• Applied data augmentation and transfer learning on a limited dataset, improving test-set robustness by 20%.
• Added post-processing for spill area estimation and distance mapping.

Stock Price Volatility Forecasting | Feb 2024 – Mar 2024
Tech Stack: Python, TensorFlow, Keras, Pandas, NumPy, Matplotlib
• Built an LSTM/GRU pipeline forecasting stock volatility from OHLCV data.
• Outperformed GARCH baselines by 18% on MAE across multiple tickers.
• Engineered features: Garman-Klass estimator, Bollinger Bands, RSI, rolling standard deviation.
• Evaluated with MAE, RMSE, and directional accuracy; visualised forecast confidence intervals.

Video Scraping Tool | Jun 2023 – Jul 2023
Tech Stack: Python, youtube-dl, BeautifulSoup, ScraperAPI, JSON
• Automated scraping of YouTube video/playlist metadata, processing 1,000+ records with ScraperAPI for anti-bot bypass.
• Output structured JSON with consistent naming conventions.

EDUCATION
Indian Institute of Information Technology, Una | May 2023 – Jun 2027 (Expected)
B.Tech, Computer Science & Engineering | GPA: 7.0
GitHub: https://github.com/devanshu119

ACHIEVEMENTS
• Ranked 3rd out of 30+ teams in IIIT Una Intra-college ICPC-style programming competition.
• Pupil on Codeforces (rating 1300+).
• AIR 11,XXX in JEE Advanced 2023 | 98th Percentile in JEE Mains 2023.
• Qualified IOQM Paper A (2023) | NSEA State Top 1% (2019).

FIT FOR SCALER AI ENGINEER ROLE
• Direct RAG production experience: reduced hallucination by 25% at Planto.ai on enterprise codebase queries.
• LLM fine-tuning: 500+ instruction pairs, 15% accuracy improvement over base model.
• Built and deployed real AI products (VSCode assistant to 3 enterprise clients).
• Strong engineering fundamentals: FastAPI, CI/CD, Docker, Python.
• Pre-final year with full availability for high-impact internship roles.
"""


def load_resume_from_text() -> list[Document]:
    """Load resume from embedded text string."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.create_documents(
        [RESUME_TEXT],
        metadatas=[{"source": "resume", "type": "resume"}],
    )
    print(f"Resume split into {len(chunks)} chunks")
    return chunks


def load_resume_from_pdf(pdf_path: str) -> list[Document]:
    """Load resume from PDF file."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{"source": "resume_pdf", "type": "resume"}],
    )
    print(f"PDF resume split into {len(chunks)} chunks")
    return chunks


def ingest_resume(pdf_path: str = None) -> int:
    """Ingest resume into Pinecone 'resume' namespace."""
    index_name = os.environ["PINECONE_INDEX_NAME"]
    get_or_create_index(index_name)

    if pdf_path and os.path.exists(pdf_path):
        docs = load_resume_from_pdf(pdf_path)
    else:
        print("No PDF found, using embedded resume text...")
        docs = load_resume_from_text()

    vs = get_vector_store(namespace="resume")
    vs.add_documents(docs)
    print(f"Ingested {len(docs)} resume chunks into Pinecone namespace 'resume'")
    return len(docs)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    pdf = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_resume(pdf)
