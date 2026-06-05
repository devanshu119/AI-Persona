"""
One-time ingestion runner: loads resume + GitHub repos into Pinecone.
Run this script once before deploying the backend.

Usage:
    python run_ingestion.py [--resume path/to/resume.pdf]
"""
import os
import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv

# Load env vars
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest.resume_loader import ingest_resume
from ingest.github_loader import ingest_github


def main():
    parser = argparse.ArgumentParser(description="Ingest resume and GitHub repos into Pinecone")
    parser.add_argument("--resume", help="Path to resume PDF", default=None)
    args = parser.parse_args()

    print("=" * 60)
    print("DEVANSHU AI PERSONA — DATA INGESTION")
    print("=" * 60)

    # Validate required env vars
    required = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"ERROR: Missing environment variables: {missing}")
        print("Please copy .env.example to .env and fill in your keys.")
        sys.exit(1)

    print("\n[1/2] Ingesting Resume...")
    resume_count = ingest_resume(args.resume)
    print(f"✓ Resume: {resume_count} chunks ingested")

    print("\n[2/2] Ingesting GitHub Repositories...")
    github_token = os.environ.get("GITHUB_TOKEN")
    github_username = os.environ.get("GITHUB_USERNAME", "devanshu119")
    github_count = ingest_github(github_token, github_username)
    print(f"✓ GitHub: {github_count} chunks ingested")

    print("\n" + "=" * 60)
    print(f"INGESTION COMPLETE")
    print(f"Total chunks: {resume_count + github_count}")
    print(f"Pinecone index: {os.environ['PINECONE_INDEX_NAME']}")
    print(f"Namespaces: resume ({resume_count}), github ({github_count})")
    print("=" * 60)
    print("\nYou can now start the backend: uvicorn main:app --reload")


if __name__ == "__main__":
    main()
