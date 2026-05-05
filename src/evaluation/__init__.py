"""
Evaluation Module
LLM-as-a-Judge implementation for evaluating system outputs.
"""
from .judge import judge_response
from .evaluator import run_evaluation

__all__ = [
    "judge_response",
    "run_evaluation",
]
