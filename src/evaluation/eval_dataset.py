"""Code for loading the evaluation dataset"""
import json
import os


def load_eval_dataset():
    """Load test questions from JSON file."""
    file_path = os.path.join(os.path.dirname(__file__), 'test_questions.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"Loaded {len(data)} test questions")
    return data


if __name__ == "__main__":
    questions = load_eval_dataset()
    for q in questions:
        print(f"[{q['difficulty']}] {q['question']}")