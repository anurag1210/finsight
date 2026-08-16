"""RAGAS Evaluation Pipeline for FinSight"""
import json
import os
import time
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
)
from src.retrieval.retriever import retrieve_hybrid
from src.generation.generator import generate_response
from src.evaluation.eval_dataset import load_eval_dataset


def run_ragas_evaluation():
    """Run RAGAS evaluation on answerable questions only."""

    # Step 1 — Load questions, skip unanswerable
    all_questions = load_eval_dataset()
    questions = [q for q in all_questions if q.get("difficulty") != "unanswerable"]

    print(f"--- RAGAS Evaluation: {len(questions)} questions ---\n")

    # Step 2 — Run each question through the pipeline
    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    for i, q in enumerate(questions):
        print(f"[{i+1}/{len(questions)}] {q['question'][:60]}...")

        start = time.time()

        # Retrieve contexts
        docs = retrieve_hybrid(q["question"])
        contexts = [doc.page_content for doc in docs]

        # Generate answer
        answer = generate_response(q["question"])

        latency = round(time.time() - start, 2)
        print(f"   Retrieved {len(contexts)} chunks | Latency: {latency}s")

        ragas_data["question"].append(q["question"])
        ragas_data["answer"].append(answer)
        ragas_data["contexts"].append(contexts)
        ragas_data["ground_truth"].append(q["ground_truth"])

    # Step 3 — Build HuggingFace Dataset (RAGAS requirement)
    dataset = Dataset.from_dict(ragas_data)

    # Step 4 — Run RAGAS evaluation
    print("\nScoring with RAGAS (this makes multiple LLM calls)...\n")

    result = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
    )
    # Step 5 — Print summary
    print("=" * 50)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 50)
    print(result)

    # Step 6 — Save detailed results
    os.makedirs("evaluation_results", exist_ok=True)
    result_df = result.to_pandas()
    result_df.to_csv("evaluation_results/ragas_report.csv", index=False)
    print(f"\nDetailed results saved to evaluation_results/ragas_report.csv")

    return result


if __name__ == "__main__":
    run_ragas_evaluation()