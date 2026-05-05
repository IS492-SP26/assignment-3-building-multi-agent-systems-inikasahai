"""
Streamlit Web Interface
Web UI for the multi-agent research system.

Run with: streamlit run src/ui/streamlit_app.py
"""
import streamlit as st
import yaml
import json
from dotenv import load_dotenv
from src.autogen_orchestrator import AutoGenOrchestrator
from src.guardrails.safety_manager import run_input_check, run_output_check, get_safety_log
from src.evaluation.judge import judge_response

load_dotenv()

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Page setup
st.set_page_config(
    page_title="HCI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("Multi-Agent HCI Research Assistant")
st.caption("Powered by AutoGen + Qwen3-8B")

# Initialize orchestrator once
@st.cache_resource
def get_orchestrator():
    return AutoGenOrchestrator(config)

orchestrator = get_orchestrator()

# Sidebar
with st.sidebar:
    st.header("Settings")
    show_traces = st.checkbox("Show agent traces", value=True)
    show_citations = st.checkbox("Show citations", value=True)
    run_judge = st.checkbox("Run LLM-as-a-Judge scoring", value=False)

    st.divider()
    st.header("Safety Log")
    safety_log = get_safety_log()
    if safety_log:
        for event in safety_log[-5:]:
            st.warning(f"**{event['event_type']}**: {event['detail']}")
    else:
        st.success("No safety events yet.")

    st.divider()
    st.header("Agents")
    st.markdown("""
- **Planner**: breaks down the query
- **Researcher**: searches web & papers
- **Writer**: synthesizes findings
- **Critic**: evaluates quality
""")

# Main query input
query = st.text_area(
    "Enter your HCI research question:",
    placeholder="e.g. What are the latest trends in conversational UI design?",
    height=100
)

col1, col2 = st.columns([1, 4])
with col1:
    submit = st.button("Research", use_container_width=True)
with col2:
    st.caption("This may take 1-2 minutes as agents collaborate.")

if submit and query:
    # Input safety check
    input_check = run_input_check(query)

    if not input_check["safe"]:
        st.error(f"**Request blocked by safety policy**")
        st.warning(f"Reason: {input_check['reason']}")
        st.info(f"Category: `{input_check['category']}`")
        st.stop()

    # Run agents
    with st.spinner("Agents are researching your query..."):
        result = orchestrator.process_query(query)

    if not result:
        st.error("The research system returned no response. Please try again.")
        st.stop()
    response = result.get("response", "")
    metadata = result.get("metadata", {})
    history = result.get("conversation_history", [])

    # Output safety check
    if not response:
        # Try getting content from conversation history instead
        for msg in reversed(history):
            if msg.get("source") in ["Critic", "Writer"] and msg.get("content"):
                response = msg.get("content", "")
                break

    output_check = run_output_check(response)
    if not output_check["safe"] and output_check["reason"] != "Empty output from model.":
        st.error("Response blocked by safety policy")
        st.warning(output_check["reason"])
        st.stop()

    safe_response = output_check["output"] if output_check["output"] else response

    # Final answer
    st.divider()
    st.subheader("Research Summary")
    st.markdown(safe_response)

    # Agent traces
    if show_traces and history:
        st.divider()
        st.subheader("Agent Traces")
        for msg in history:
            source = msg.get("source", "unknown")
            content = msg.get("content", "")
            if not content:
                continue
            icons = {
                "Planner": "📋",
                "Researcher": "🔍",
                "Writer": "✍️",
                "Critic": "🧐"
            }
            icon = icons.get(source, "🤖")
            with st.expander(f"{icon} {source}"):
                st.markdown(content)

    # Citations
    if show_citations:
        st.divider()
        st.subheader("Sources")
        findings = metadata.get("research_findings", [])
        if findings:
            for finding in findings:
                lines = finding.split("\n")
                for line in lines:
                    if "http" in line:
                        st.markdown(f"- {line.strip()}")
        else:
            st.info("No sources extracted.")

    # Metadata
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Messages", metadata.get("num_messages", 0))
    col2.metric("Sources", metadata.get("num_sources", 0))
    col3.metric("Agents", len(metadata.get("agents_involved", [])))

    # LLM Judge
    if run_judge:
        st.divider()
        st.subheader("LLM-as-a-Judge Evaluation")
        with st.spinner("Scoring response..."):
            scores = judge_response(query, safe_response)

        avg = scores.get("average_overall", 0)
        st.metric("Average Score", f"{avg}/10")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Judge 1 (Relevance & Clarity)**")
            j1 = scores.get("judge_1", {})
            for k, v in j1.items():
                if k not in ["feedback", "error", "overall"] and isinstance(v, (int, float)):
                    st.progress(v / 10, text=f"{k}: {v}/10")
            if "feedback" in j1:
                st.caption(j1["feedback"])

        with col2:
            st.markdown("**Judge 2 (Academic Rigor)**")
            j2 = scores.get("judge_2", {})
            for k, v in j2.items():
                if k not in ["feedback", "error", "overall"] and isinstance(v, (int, float)):
                    st.progress(v / 10, text=f"{k}: {v}/10")
            if "feedback" in j2:
                st.caption(j2["feedback"])

    # Export session
    st.divider()
    session_data = {
        "query": query,
        "response": safe_response,
        "conversation_history": history,
        "metadata": metadata,
    }
    st.download_button(
        label="⬇Export Session (JSON)",
        data=json.dumps(session_data, indent=2),
        file_name="research_session.json",
        mime="application/json"
    )