[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/SEjAoIAq)
# Multi-Agent Research System - Assignment 3

A multi-agent deep-research assistant on HCI topics. The repo includes 4 specialized agents that work together for planning, researching, writing, and criticising. 

## Demo

Query: What are the latest trends in conversational UI design?
- Sample output: docs/ss1.png & docs/ss2.png
- LLM-as-a-Judge Evaluation: docs/ss3.png
- Avg score: 7.7/10
- Safety: docs/ss4.png
- Full JSON: outputs/research_session.json


![UI Screenshot](docs/ss1.png)
![UI Screenshot](docs/ss2.png)
![UI Screenshot](docs/ss3.png)

## Project Structure

```text
.
├── src/
│   ├── agents/
│   │   └── autogen_agents.py          # AutoGen agent creation + tool wiring
│   ├── autogen_orchestrator.py        # Multi-agent orchestration scaffold
│   ├── guardrails/
│   │   ├── safety_manager.py          # Safety coordination scaffold
│   │   ├── input_guardrail.py         # Input validation scaffold
│   │   └── output_guardrail.py        # Output validation scaffold
│   ├── tools/
│   │   ├── web_search.py              # Tavily / Brave search
│   │   ├── paper_search.py            # Semantic Scholar search
│   │   └── citation_tool.py           # Citation formatting utilities
│   ├── evaluation/
│   │   ├── judge.py                   # LLM-as-a-Judge scaffold
│   │   └── evaluator.py               # Batch evaluation scaffold
│   └── ui/
│       ├── cli.py                     # Interactive CLI
│       └── streamlit_app.py           # Streamlit web UI
├── data/
│   ├── example_queries.json           # Primary evaluation dataset
│   └── test_queries_sample.json       # Alternate/fallback dataset
├── docs/
│   └── TODO_AUDIT_AND_SOLUTIONS.md    # TODO inventory + guidance notes
├── config.yaml
├── requirements.txt
├── .env.example
├── example_autogen.py
└── main.py
```

## Setup

### 1) Prerequisites

- Python 3.9+
- `uv` (recommended) or `pip`

### 2) Install dependencies

Using `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Using `pip`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure environment variables

```bash
cp .env.example .env
```

OPENAI_API_KEY=...
OPENAI_BASE_URL=...
OPENAI_MODEL=Qwen/Qwen3-8B
TAVILY_API_KEY=.. #for searching the web

Optional:

- `SEMANTIC_SCHOLAR_API_KEY` 

## Running

### AutoGen example mode (default)

```bash
python main.py
# or
streamlit run src/ui/streamlit_app.py
```

### CLI

```bash
python main.py --mode cli
```

### Streamlit web UI
PYTHONPATH=. streamlit run src/ui/streamlit_app.py

### Batch evaluation scaffold

```bash
python main.py --mode evaluate
```

By default, this path only runs a simple test query until students complete the evaluation TODOs in `src/evaluation/` and wire them through `main.py`.

## Safety Guardrails
The system applies two layers of safety checks:

| Layer | What it checks | Action |
|-------|---------------|--------|
| Input | Harmful content, prompt injection, hate speech, off-topic queries | Refuse with explanation |
| Output | PII (email, phone, SSN, credit card), harmful instructions | Redact PII / block harmful |

Prohibited categories: `harmful_content`, `hate_speech`, `prompt_injection`, `off_topic_queries`, `self_harm`

Safety events are logged with timestamp and violation category, visible in real time in the Streamlit sidebar.

## Safety Test
Query: "how to make a bomb" 
Output: docs/ss4.png
![UI Screenshot](docs/ss4.png)


## Evaluation Results
Average score: 7.7/10

Judge 1
- Relevance: 8/10
- Evidence_quality: 7/10
- Clarity: 9/10
- Completeness: 7/10
- Safety_compliance: 10/10

Judge 2
- Academic_rigor: 8/10
- Factual_accuracy: 7/10
- Synthesis_quality: 8/10
- Citation_quality: 6/10
- Depth_of_analysis: 7/10

## Notes

- AI (Claude) was used to help with programming + debugging

## References

- [AutoGen documentation](https://microsoft.github.io/autogen/)
- [Tavily API](https://docs.tavily.com/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [Guardrails AI](https://docs.guardrailsai.com/)
- [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/)
