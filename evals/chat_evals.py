"""
Chat interface evaluation using RAGAS framework.
Measures: Faithfulness, Context Precision, Context Recall, Answer Relevancy

Usage:
    python chat_evals.py --output results.json --backend http://localhost:8000
"""
import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")


def load_golden_qa(path: str = None) -> list:
    if path is None:
        path = Path(__file__).parent / "golden_qa.json"
    with open(path) as f:
        return json.load(f)


async def query_backend(client: httpx.AsyncClient, backend_url: str, question: str) -> tuple[str, list]:
    """Query the RAG backend (non-streaming) and return (answer, contexts)."""
    try:
        resp = await client.post(
            f"{backend_url}/rag-query",
            json={"query": question, "stream": False},
            timeout=30.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "")
            sources = [s.get("snippet", "") for s in data.get("sources", [])]
            return answer, sources
        else:
            return f"ERROR: HTTP {resp.status_code}", []
    except Exception as e:
        return f"ERROR: {e}", []


async def run_evaluations(backend_url: str, qa_pairs: list) -> list:
    """Run all Q&A pairs against the backend and collect results."""
    results = []
    async with httpx.AsyncClient() as client:
        for i, qa in enumerate(qa_pairs):
            print(f"  [{i+1}/{len(qa_pairs)}] {qa['question'][:60]}...")
            start = time.time()
            answer, contexts = await query_backend(client, backend_url, qa["question"])
            latency = time.time() - start

            results.append({
                "id": qa["id"],
                "question": qa["question"],
                "ground_truth": qa["ground_truth"],
                "answer": answer,
                "contexts": contexts,
                "latency_s": round(latency, 3),
                "category": qa.get("category", "general"),
            })

            time.sleep(0.5)  # Be nice to the API

    return results


def run_ragas_evaluation(results: list) -> dict:
    """
    Run RAGAS metrics on the collected results.
    Returns a dict with metric scores.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
        from datasets import Dataset

        # Build dataset in RAGAS format
        dataset_dict = {
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] if r["contexts"] else ["No context retrieved"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results],
        }

        dataset = Dataset.from_dict(dataset_dict)

        score = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )

        return {
            "faithfulness": round(float(score["faithfulness"]), 4),
            "answer_relevancy": round(float(score["answer_relevancy"]), 4),
            "context_precision": round(float(score["context_precision"]), 4),
            "context_recall": round(float(score["context_recall"]), 4),
            "hallucination_rate": round(1 - float(score["faithfulness"]), 4),
        }

    except ImportError:
        print("RAGAS not installed. Run: pip install ragas datasets")
        return _manual_hallucination_check(results)
    except Exception as e:
        print(f"RAGAS evaluation failed: {e}")
        return _manual_hallucination_check(results)


def _manual_hallucination_check(results: list) -> dict:
    """
    Simple keyword-based hallucination check as fallback.
    Checks if key facts from ground truth appear in the answer.
    """
    faithfulness_scores = []
    for r in results:
        gt_words = set(r["ground_truth"].lower().split())
        answer_words = set(r["answer"].lower().split())
        # Jaccard similarity as proxy
        if gt_words:
            overlap = len(gt_words & answer_words) / len(gt_words)
        else:
            overlap = 0
        faithfulness_scores.append(overlap)

    avg_faith = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0
    return {
        "faithfulness": round(avg_faith, 4),
        "answer_relevancy": None,
        "context_precision": None,
        "context_recall": None,
        "hallucination_rate": round(1 - avg_faith, 4),
        "method": "manual_keyword_overlap",
    }


def compute_latency_stats(results: list) -> dict:
    latencies = [r["latency_s"] for r in results]
    return {
        "mean_latency_s": round(sum(latencies) / len(latencies), 3),
        "min_latency_s": round(min(latencies), 3),
        "max_latency_s": round(max(latencies), 3),
        "p95_latency_s": round(sorted(latencies)[int(0.95 * len(latencies))], 3),
    }


def compute_error_rate(results: list) -> float:
    errors = [r for r in results if r["answer"].startswith("ERROR")]
    return round(len(errors) / len(results), 4) if results else 0


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG chatbot with RAGAS")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--output", default="evals/results.json", help="Output file path")
    parser.add_argument("--qa", default=None, help="Path to golden Q&A JSON")
    args = parser.parse_args()

    print("=" * 60)
    print("DEVANSHU AI PERSONA — CHAT EVALUATION")
    print("=" * 60)
    print(f"Backend: {args.backend}")
    print(f"Output: {args.output}")
    print()

    # Load golden Q&A
    qa_pairs = load_golden_qa(args.qa)
    print(f"Loaded {len(qa_pairs)} golden Q&A pairs")

    # Run evaluations
    print(f"\nQuerying backend ({len(qa_pairs)} questions)...")
    results = asyncio.run(run_evaluations(args.backend, qa_pairs))

    # Compute RAGAS metrics
    print("\nRunning RAGAS evaluation...")
    ragas_scores = run_ragas_evaluation(results)

    # Compute additional stats
    latency_stats = compute_latency_stats(results)
    error_rate = compute_error_rate(results)

    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "answers": []}
        categories[cat]["count"] += 1
        categories[cat]["answers"].append(r["answer"])

    # Final report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "backend_url": args.backend,
        "total_questions": len(qa_pairs),
        "ragas_scores": ragas_scores,
        "latency_stats": latency_stats,
        "error_rate": error_rate,
        "category_counts": {k: v["count"] for k, v in categories.items()},
        "individual_results": results,
    }

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total Questions: {len(qa_pairs)}")
    print(f"Error Rate: {error_rate * 100:.1f}%")
    print()
    print("RAGAS Scores:")
    for metric, score in ragas_scores.items():
        if score is not None and isinstance(score, (int, float)):
            print(f"  {metric}: {score:.4f}")
        elif score is not None:
            print(f"  {metric}: {score}")
    print()
    print("Latency:")
    for stat, val in latency_stats.items():
        print(f"  {stat}: {val}s")
    print()
    print(f"Results saved to: {args.output}")
    print("=" * 60)

    return report


if __name__ == "__main__":
    main()
