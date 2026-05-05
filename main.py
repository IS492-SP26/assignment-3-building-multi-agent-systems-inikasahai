"""
Main Entry Point
Can be used to run the system or evaluation.

Usage:
  python main.py --mode cli           # Run CLI interface
  python main.py --mode web           # Run web interface
  python main.py --mode evaluate      # Run evaluation
"""
import argparse
import yaml
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def run_autogen(config):
    from src.autogen_orchestrator import AutoGenOrchestrator
    from src.guardrails.safety_manager import run_input_check, run_output_check

    orchestrator = AutoGenOrchestrator(config)
    print("\n🔬 Multi-Agent HCI Research Assistant")
    print("=" * 50)

    query = input("\nEnter your research query: ").strip()

    # Input check
    check = run_input_check(query)
    if not check["safe"]:
        print(f"\n🚫 Blocked: {check['reason']}")
        return

    print("\n⏳ Agents are working...\n")
    result = orchestrator.process_query(query)

    # Output check
    out = run_output_check(result.get("response", ""))
    if not out["safe"]:
        print(f"\n🚫 Output blocked: {out['reason']}")
        return

    print("\n" + "=" * 50)
    print("FINAL RESPONSE")
    print("=" * 50)
    print(out["output"])

    meta = result.get("metadata", {})
    print(f"\n📊 Messages: {meta.get('num_messages', 0)} | Sources: {meta.get('num_sources', 0)}")

def run_web(config):
    import subprocess
    import sys
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/ui/streamlit_app.py",
        "--server.headless", "false"
    ], env={**__import__('os').environ, "PYTHONPATH": "."})

def run_evaluate(config):
    import json
    from src.autogen_orchestrator import AutoGenOrchestrator
    from src.evaluation.evaluator import run_evaluation

    print("\n📊 Running batch evaluation...")

    with open("data/example_queries.json") as f:
        query_data = json.load(f)

    queries = [q["query"] for q in query_data]
    orchestrator = AutoGenOrchestrator(config)
    report = run_evaluation(orchestrator, queries)

    print("\n" + "=" * 50)
    print("EVALUATION REPORT")
    print("=" * 50)
    agg = report["aggregate"]
    print(f"Total queries:  {agg['total_queries']}")
    print(f"Average score:  {agg['average_score']}/10")
    print(f"Min score:      {agg['min_score']}/10")
    print(f"Max score:      {agg['max_score']}/10")

    print("\nPer-query results:")
    for r in report["results"]:
        score = r["scores"].get("average_overall", 0)
        print(f"  [{score}/10] {r['query'][:60]}...")

    # Save report
    with open("outputs/evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✅ Report saved to outputs/evaluation_report.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent HCI Research Assistant")
    parser.add_argument(
        "--mode",
        choices=["autogen", "web", "evaluate"],
        default="web",
        help="Run mode: autogen (CLI), web (Streamlit), evaluate (batch)"
    )
    args = parser.parse_args()
    config = load_config()

    if args.mode == "autogen":
        run_autogen(config)
    elif args.mode == "web":
        run_web(config)
    elif args.mode == "evaluate":
        run_evaluate(config)