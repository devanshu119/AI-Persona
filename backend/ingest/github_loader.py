"""
GitHub repository loader.
Fetches READMEs, file trees, and key source files from Devanshu's public GitHub repos.
Ingests into Pinecone 'github' namespace.
"""
import os
import sys
import time
from pathlib import Path

from github import Github, GithubException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.pinecone_client import get_vector_store, get_or_create_index

# Files worth indexing beyond README
INTERESTING_EXTENSIONS = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".ts", ".js"}
MAX_FILE_SIZE = 50_000  # bytes — skip large files
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}

# Hard-coded fallback for key repos in case GitHub rate-limits
FALLBACK_REPO_DOCS = [
    {
        "repo": "devanshu119/oil-spill-detection",
        "content": """
Repository: oil-spill-detection
Owner: devanshu119
Description: Oil Spill Detection using Computer Vision and SAR satellite imagery.
Tech Stack: Python, PyTorch, OpenCV, Streamlit, U-Net, DeepLabv3, CNN
Purpose: Detect and segment oil spills from SAR (Synthetic Aperture Radar) satellite images using deep learning.
Design: Trained multiple segmentation architectures (U-Net, DeepLabv3, CNN). Achieved >90% IoU on test set.
Data augmentation and transfer learning applied to improve robustness on limited dataset.
Deployed as Streamlit web app with real-time segmentation overlay.
Post-processing for spill area estimation and GPS distance mapping.
What I'd do differently: Use a transformer-based segmentation model (SegFormer) and add uncertainty quantification
to flag low-confidence predictions. Would also integrate a proper MLflow experiment tracker.
        """,
    },
    {
        "repo": "devanshu119/stock-volatility-forecasting",
        "content": """
Repository: stock-volatility-forecasting
Owner: devanshu119
Description: Stock Price Volatility Forecasting using LSTM/GRU neural networks.
Tech Stack: Python, TensorFlow, Keras, Pandas, NumPy, Matplotlib
Purpose: Forecast short-term stock price volatility from historical OHLCV data.
Design: LSTM and GRU networks trained on engineered financial features (Garman-Klass estimator,
Bollinger Bands, RSI, rolling standard deviation). Outperformed GARCH baseline by 18% on MAE.
Evaluation metrics: MAE, RMSE, directional accuracy, confidence interval visualisation.
What I'd do differently: Incorporate attention mechanisms (Temporal Fusion Transformer) and add
a proper backtesting harness to evaluate trading signal quality, not just statistical error.
        """,
    },
    {
        "repo": "devanshu119/video-scraping-tool",
        "content": """
Repository: video-scraping-tool
Owner: devanshu119
Description: YouTube video and playlist metadata scraper.
Tech Stack: Python, youtube-dl, BeautifulSoup, ScraperAPI, JSON
Purpose: Automated bulk scraping of YouTube video/playlist metadata for dataset creation.
Design: Uses ScraperAPI for anti-bot bypass. Processes 1000+ records per run.
Outputs structured JSON with consistent field naming. Supports both individual videos and playlists.
What I'd do differently: Use the official YouTube Data API v3 where rate limits allow, falling back
to ScraperAPI only for public data that the official API doesn't expose. Add async processing for 10x throughput.
        """,
    },
]


def fetch_repo_documents(github_token: str, username: str) -> list[Document]:
    """Fetch real repo documents from GitHub API."""
    g = Github(github_token)
    docs: list[Document] = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)

    try:
        user = g.get_user(username)
        repos = list(user.get_repos(type="public"))
        print(f"Found {len(repos)} public repos for {username}")

        for repo in repos:
            if repo.fork:
                continue  # Skip forks

            print(f"  Processing: {repo.full_name}")
            repo_meta = {
                "source": f"github:{repo.full_name}",
                "repo": repo.full_name,
                "type": "github",
                "stars": repo.stargazers_count,
                "language": repo.language or "Unknown",
                "description": repo.description or "",
            }

            # Always get README
            try:
                readme = repo.get_readme()
                readme_content = readme.decoded_content.decode("utf-8", errors="ignore")
                readme_header = f"""
Repository: {repo.full_name}
Description: {repo.description or 'No description'}
Language: {repo.language or 'Unknown'}
Stars: {repo.stargazers_count}
URL: {repo.html_url}

README:
{readme_content}
"""
                chunks = splitter.create_documents(
                    [readme_header],
                    metadatas=[{**repo_meta, "file": "README.md"}],
                )
                docs.extend(chunks)
            except GithubException:
                # No README — add basic metadata doc
                basic = f"Repository {repo.full_name}: {repo.description or 'No description'}. Language: {repo.language}."
                docs.append(Document(page_content=basic, metadata=repo_meta))

            # Get key source files (limit to avoid rate limiting)
            try:
                contents = repo.get_contents("")
                files_processed = 0
                while contents and files_processed < 10:
                    file_content = contents.pop(0)
                    if file_content.type == "dir":
                        if file_content.name not in SKIP_DIRS:
                            try:
                                contents.extend(repo.get_contents(file_content.path))
                            except GithubException:
                                pass
                    else:
                        ext = Path(file_content.name).suffix
                        if ext in INTERESTING_EXTENSIONS and file_content.size < MAX_FILE_SIZE:
                            try:
                                text = file_content.decoded_content.decode("utf-8", errors="ignore")
                                file_header = f"File: {file_content.path} in {repo.full_name}\n\n{text}"
                                file_chunks = splitter.create_documents(
                                    [file_header],
                                    metadatas=[{**repo_meta, "file": file_content.path}],
                                )
                                docs.extend(file_chunks)
                                files_processed += 1
                            except Exception:
                                pass

            except GithubException as e:
                print(f"    Could not list contents: {e}")

            time.sleep(0.5)  # Rate limit courtesy

    except Exception as e:
        print(f"GitHub API error: {e}")
        return []

    print(f"Total GitHub documents: {len(docs)}")
    return docs


def get_fallback_documents() -> list[Document]:
    """Return fallback documents if GitHub API is unavailable."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
    docs = []
    for repo_data in FALLBACK_REPO_DOCS:
        chunks = splitter.create_documents(
            [repo_data["content"]],
            metadatas=[{"source": f"github:{repo_data['repo']}", "type": "github_fallback"}],
        )
        docs.extend(chunks)
    return docs


def ingest_github(github_token: str = None, username: str = "devanshu119") -> int:
    """Ingest GitHub repos into Pinecone 'github' namespace."""
    index_name = os.environ["PINECONE_INDEX_NAME"]
    get_or_create_index(index_name)

    if github_token:
        docs = fetch_repo_documents(github_token, username)
    else:
        print("No GitHub token — using fallback repo descriptions")
        docs = []

    if not docs:
        print("Using fallback GitHub documents...")
        docs = get_fallback_documents()

    if docs:
        vs = get_vector_store(namespace="github")
        vs.add_documents(docs)
        print(f"Ingested {len(docs)} GitHub chunks into Pinecone namespace 'github'")

    return len(docs)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("GITHUB_USERNAME", "devanshu119")
    ingest_github(token, username)
