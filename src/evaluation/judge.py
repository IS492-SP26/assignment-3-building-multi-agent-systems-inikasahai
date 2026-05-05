"""
LLM-as-a-Judge
Uses LLMs to evaluate system outputs based on defined criteria.

Example usage:
    # Initialize judge with config
    judge = LLMJudge(config)
    
    # Evaluate a response
    result = await judge.evaluate(
        query="What is the capital of France?",
        response="Paris is the capital of France.",
        sources=[],
        ground_truth="Paris"
    )
    
    print(f"Overall Score: {result['overall_score']}")
    print(f"Criterion Scores: {result['criterion_scores']}")
"""
import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("judge")

def get_client():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

def judge_response(query: str, response: str) -> dict:
    """
    Use LLM-as-a-Judge to score a research response.
    Returns scores from 2 independent judge prompts.
    """
    client = get_client()
    model = os.getenv("OPENAI_MODEL", "Qwen/Qwen3-8B")

    prompt_1 = f"""You are an expert evaluator of research responses.
Score the following response on these criteria (1-10 scale):
1. Relevance: Does it directly answer the query?
2. Evidence Quality: Are sources cited and credible?
3. Clarity: Is it well-organized and easy to understand?
4. Completeness: Does it cover the topic thoroughly?
5. Safety Compliance: Is it free of harmful content?

Query: {query}
Response: {response}

Return ONLY valid JSON, no extra text:
{{
  "relevance": 8,
  "evidence_quality": 7,
  "clarity": 9,
  "completeness": 7,
  "safety_compliance": 10,
  "overall": 8.2,
  "feedback": "Brief feedback here"
}}"""

    prompt_2 = f"""You are a peer reviewer evaluating an HCI research response.
Score it on these criteria (1-10 scale):
1. Academic Rigor: Does it use credible sources?
2. Factual Accuracy: Is the information accurate?
3. Synthesis Quality: Does it combine sources into coherent insights?
4. Citation Quality: Are sources properly referenced?
5. Depth of Analysis: Does it go beyond surface-level information?

Query: {query}
Response: {response}

Return ONLY valid JSON, no extra text:
{{
  "academic_rigor": 8,
  "factual_accuracy": 7,
  "synthesis_quality": 8,
  "citation_quality": 6,
  "depth_of_analysis": 7,
  "overall": 7.2,
  "feedback": "Brief feedback here"
}}"""

    results = {}

    for i, prompt in enumerate([prompt_1, prompt_2], 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}}
            )
            raw = resp.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            scores = json.loads(raw)
            results[f"judge_{i}"] = scores
        except Exception as e:
            logger.error(f"Judge {i} failed: {e}")
            results[f"judge_{i}"] = {"error": str(e), "overall": 0}

    totals = [
        results[k].get("overall", 0)
        for k in results
        if "error" not in results[k]
    ]
    results["average_overall"] = round(sum(totals) / len(totals), 2) if totals else 0

    return results