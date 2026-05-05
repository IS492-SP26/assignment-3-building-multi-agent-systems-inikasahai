import re
import logging

logger = logging.getLogger("input_guardrail")

BLOCKED_PATTERNS = [
    # Harmful content
    r"\b(kill|murder|harm|hurt|attack|bomb|weapon|explosive)\b",
    # Hate speech
    r"\b(hate|racist|sexist|discriminat)\b",
    # Prompt injection attempts
    r"(ignore previous|ignore all instructions|you are now|pretend you are|jailbreak)",
    # Self harm
    r"\b(suicide|self.harm|self.destruct)\b",
    # Illegal activity
    r"\b(illegal|hack|crack|steal|fraud|scam)\b",
]

OFF_TOPIC_KEYWORDS = [
    "lottery", "casino", "gambling", "dating", "celebrity gossip",
    "stock tips", "crypto pump"
]

def check_input(user_input: str) -> dict:
    """
    Check user input for unsafe or inappropriate content.
    Returns a dict with 'safe' (bool), 'reason' (str), 'category' (str).
    """
    if not user_input or not user_input.strip():
        return {
            "safe": False,
            "reason": "Empty input received.",
            "category": "empty_input"
        }

    text = user_input.lower()

    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Blocked input matched pattern: {pattern}")
            return {
                "safe": False,
                "reason": "Your request contains content that violates our safety policy.",
                "category": "harmful_content"
            }

    # Check off-topic
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in text:
            logger.warning(f"Off-topic keyword detected: {keyword}")
            return {
                "safe": False,
                "reason": "This system is designed for HCI research queries only.",
                "category": "off_topic"
            }

    # Check minimum length
    if len(user_input.strip()) < 5:
        return {
            "safe": False,
            "reason": "Query is too short. Please provide more detail.",
            "category": "too_short"
        }

    return {"safe": True, "reason": "", "category": ""}
