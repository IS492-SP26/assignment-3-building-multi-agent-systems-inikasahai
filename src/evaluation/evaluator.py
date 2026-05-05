"""
System Evaluator
Runs batch evaluations and generates reports.

Example usage:
    # Load config
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Initialize evaluator with orchestrator
    evaluator = SystemEvaluator(config, orchestrator=my_orchestrator)
    
    # Run evaluation
    report = await evaluator.evaluate_system("data/test_queries.json")
    
    # Results are automatically saved to outputs/
"""

import json
import logging
from src.evaluation.judge import judge_response

logger = logging.getLogger("evaluator")

def run_evaluation(orchestrator, queries: list) -> dict:
    """
    Run the multi-agent system on a list of queries and judge each response.
    """
    results = []

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Evaluating: {query}")
        try:
            result = orchestrator.process_query(query)
            response = result.get("response", "")

            scores = judge_response(query, response)

            results.append({
                "query": query,
                "response": response[:500] + "..." if len(response) > 500 else response,
                "scores": scores
            })

            print(f"  Average score: {scores.get('average_overall', 0)}/10")

        except Exception as e:
            logger.error(f"Evaluation failed for query: {query} — {e}")
            results.append({
                "query": query,
                "response": "",
                "scores": {"error": str(e), "average_overall": 0}
            })

    all_scores = [r["scores"].get("average_overall", 0) for r in results]
    aggregate = {
        "total_queries": len(results),
        "average_score": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
        "min_score": min(all_scores) if all_scores else 0,
        "max_score": max(all_scores) if all_scores else 0,
    }

    return {
        "results": results,
        "aggregate": aggregate
    }
