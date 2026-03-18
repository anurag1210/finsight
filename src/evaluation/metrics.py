"""LLM-as-a-judge metrics for evaluation."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from langchain_openai import ChatOpenAI

from src.config import LLM_MODEL, OPENAI_API_KEY


@dataclass(frozen=True)
class JudgeResult:
    score: float
    verdict: str
    rationale: str


_SYSTEM_PROMPT = (
    "You are a strict evaluator for a financial QA system. "
    "Return ONLY valid JSON with keys: score (number 0..1), "
    "verdict (one of: correct, partial, incorrect), rationale (short string). "
    "Do not include any extra text."
)


def _build_user_prompt(
    question: str,
    expected_answer: str,
    generated_answer: str,
    difficulty: str | None,
) -> str:
    rubric = (
        "Rubric:\n"
        "1.0 = fully correct and complete, no hallucinations.\n"
        "0.5 = partially correct (some correct facts but missing key points or minor errors).\n"
        "0.0 = incorrect or contradicts expected, or fabricates facts.\n"
        "If difficulty is 'unanswerable', score 1.0 only if the answer clearly states the "
        "information is not found/insufficient in the sources; otherwise 0.0.\n"
    )
    return (
        f"{rubric}\n"
        f"Question: {question}\n"
        f"Difficulty: {difficulty or 'unknown'}\n"
        f"Expected Answer: {expected_answer}\n"
        f"Generated Answer: {generated_answer}\n"
    )


def _parse_judge_json(raw: str) -> JudgeResult:
    """Parse JSON from model output, tolerating extra text if present."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))

    score = float(data.get("score", 0.0))
    score = max(0.0, min(1.0, score))
    verdict = str(data.get("verdict", "incorrect")).strip().lower()
    if verdict not in {"correct", "partial", "incorrect"}:
        verdict = "incorrect"
    rationale = str(data.get("rationale", "")).strip()
    return JudgeResult(score=score, verdict=verdict, rationale=rationale)


def llm_judge(
    question: str,
    expected_answer: str,
    generated_answer: str,
    difficulty: str | None = None,
    model: str = LLM_MODEL,
) -> JudgeResult:
    """Use an LLM to grade the generated answer against the expected answer."""
    llm = ChatOpenAI(
        model=model,
        api_key=OPENAI_API_KEY,
        temperature=0.0,
        max_tokens=300,
    )
    messages = [
        ("system", _SYSTEM_PROMPT),
        (
            "human",
            _build_user_prompt(
                question=question,
                expected_answer=expected_answer,
                generated_answer=generated_answer,
                difficulty=difficulty,
            ),
        ),
    ]
    response = llm.invoke(messages)
    return _parse_judge_json(response.content)


def llm_judge_score(
    question: str,
    expected_answer: str,
    generated_answer: str,
    difficulty: str | None = None,
    model: str = LLM_MODEL,
) -> float:
    """Return only the numeric score (0..1) from the LLM judge."""
    return llm_judge(
        question=question,
        expected_answer=expected_answer,
        generated_answer=generated_answer,
        difficulty=difficulty,
        model=model,
    ).score
