import logging
import json
from datetime import datetime
from src.guardrails.input_guardrail import check_input
from src.guardrails.output_guardrail import check_output

logger = logging.getLogger("safety_manager")

safety_event_log = []

def log_safety_event(event_type: str, detail: str, category: str = ""):
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "detail": detail,
        "category": category
    }
    safety_event_log.append(event)
    logger.warning(f"SAFETY EVENT [{event_type}]: {detail}")

def run_input_check(user_input: str) -> dict:
    """
    Run input safety check and log any violations.
    Returns dict with 'safe', 'reason', 'category'.
    """
    result = check_input(user_input)
    if not result["safe"]:
        log_safety_event(
            event_type="INPUT_BLOCKED",
            detail=result["reason"],
            category=result["category"]
        )
    return result

def run_output_check(output: str) -> dict:
    """
    Run output safety check and log any violations.
    Returns dict with 'safe', 'output', 'reason'.
    """
    result = check_output(output)
    if not result["safe"]:
        log_safety_event(
            event_type="OUTPUT_BLOCKED",
            detail=result["reason"],
            category="unsafe_output"
        )
    elif result["output"] != output:
        log_safety_event(
            event_type="OUTPUT_REDACTED",
            detail="PII or sensitive content was redacted.",
            category="pii_redaction"
        )
    return result

def get_safety_log() -> list:
    return safety_event_log