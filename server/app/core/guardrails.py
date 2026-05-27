BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "execute shell",
    "rm -rf",
    "drop table",
    "delete from",
    "jailbreak",
    "forget your instructions",
    "you are now",
    "act as",
    "pretend you are",
]


def detect_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in BLOCKED_PATTERNS)
