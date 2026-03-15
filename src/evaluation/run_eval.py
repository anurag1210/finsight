"""Evaluation runner for the RAG application"""
import json
import os
import re
import time
from src.generation.generator import generate_response
from src.evaluation.eval_dataset import load_eval_dataset


def extract_key_facts(expected_answer):
    """Extract numbers and key terms from expected answer."""
    # Find all dollar amounts and numbers
    numbers = re.findall(r'\$?[\d,]+\.?\d*', expected_answer)
    # Find key phrases (split by commas for list-type answers)
    phrases = [p.strip() for p in expected_answer.split(',') if len(p.strip()) > 3]
    return numbers + phrases


def check_answer(expected, generated, difficulty):
    """Check if the generated answer matches expected answer."""
    if difficulty == "unanswerable":
        return 1.0 if "information not found" in generated.lower() else 0.0
    
    key_facts = extract_key_facts(expected)
    if not key_facts:
        return 0.0
    
    matches = sum(1 for fact in key_facts if fact.lower() in generated.lower())
    return matches / len(key_facts)


def evaluate_rag():
    """Run evaluation across all test questions."""
    questions = load_eval_dataset()
    results = []
    
    print(f"--- Starting Evaluation on {len(questions)} samples ---\n")
    
    for i, q in enumerate(questions):
        print(f"[{i+1}/{len(questions)}] Processing: {q['question'][:60]}...")
        
        start_time = time.time()
        generated_answer = generate_response(q['question'])
        latency = round(time.time() - start_time, 2)
        
        score = check_answer(q['expected_answer'], generated_answer, q['difficulty'])
        
        results.append({
            "question": q['question'],
            "difficulty": q['difficulty'],
            "expected": q['expected_answer'],
            "generated": generated_answer,
            "score": score,
            "latency_sec": latency
        })
        
        print(f"   Score: {score:.2f} | Latency: {latency}s")

    # Print Summary Report
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    
    total = len(results)
    avg_score = sum(r['score'] for r in results) / total
    avg_latency = sum(r['latency_sec'] for r in results) / total
    
    print(f"Total Questions: {total}")
    print(f"Average Score: {avg_score:.2%}")
    print(f"Average Latency: {avg_latency:.2f}s")
    
    # Grouped by difficulty
    print("\nBy Difficulty:")
    for diff in ["easy", "medium", "hard", "unanswerable"]:
        diff_results = [r for r in results if r["difficulty"] == diff]
        if diff_results:
            acc = sum(r['score'] for r in diff_results) / len(diff_results)
            print(f"  {diff.capitalize()}: {acc:.2%} ({len(diff_results)} questions)")

    # Save results
    os.makedirs('evaluation_results', exist_ok=True)
    with open('evaluation_results/eval_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to evaluation_results/eval_report.json")


if __name__ == "__main__":
    evaluate_rag()