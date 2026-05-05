import re
import logging

logger = logging.getLogger("output_guardrail")

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",           # SSN
    r"\b\d{16}\b",                        # Credit card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",   # Phone number
]

UNSAFE_OUTPUT_PATTERNS = [
    r"(how to make a bomb|how to hack|how to steal)",
    r"(kill yourself|end your life)",
]

MAX_LENGTH = 4000

def check_output(output: str) -> dict:
    """
    Check model output for unsafe content or PII.
    Returns dict with 'safe' (bool), 'output' (str), 'reason' (str).
    """
    if not output or not output.strip():
        return {
            "safe": False,
            "output": "",
            "reason": "Empty output from model."
        }

    # Check unsafe patterns
    for pattern in UNSAFE_OUTPUT_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            logger.warning(f"Unsafe output pattern detected: {pattern}")
            return {
                "safe": False,
                "output": "",
                "reason": "Output contained unsafe content and was blocked."
            }

    # Redact PII
    redacted = output
    for pattern in PII_PATTERNS:
        redacted = re.sub(pattern, "[REDACTED]", redacted)

    if redacted != output:
        logger.info("PII detected and redacted from output.")

    # Truncate if too long
    if len(redacted) > MAX_LENGTH:
        redacted = redacted[:MAX_LENGTH] + "\n\n[Response truncated for safety.]"

    return {
        "safe": True,
        "output": redacted,
        "reason": ""
    }