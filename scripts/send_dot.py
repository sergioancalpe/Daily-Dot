"""Send a dot message to the Anthropic API using two separate API keys.

Each key triggers an independent call to claude-haiku-4-5-20251001. Both calls
always execute, even if one fails. Results are logged to logs/YYYY-MM-DD.txt
and printed to stdout for visibility in GitHub Actions.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"
MESSAGE = "."
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def call_api(key_label: str, api_key: str) -> dict:
    """Call the Anthropic API with the given key. Never raises — errors are captured."""
    result = {
        "key_label": key_label,
        "message_sent": MESSAGE,
        "response": None,
        "error": None,
    }

    if not api_key:
        result["error"] = f"{key_label}: environment variable is empty or not set"
        return result

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": MESSAGE}],
        )
        text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        result["response"] = "".join(text_parts) if text_parts else "<no text content>"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def format_result(result: dict) -> str:
    lines = [
        f"--- {result['key_label']} ---",
        f"Message sent: {result['message_sent']}",
    ]
    if result["error"]:
        lines.append(f"Error: {result['error']}")
    else:
        lines.append(f"Response: {result['response']}")
    return "\n".join(lines)


def main() -> int:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S UTC")

    key1 = os.environ.get("ANTHROPIC_API_KEY_1", "")
    key2 = os.environ.get("ANTHROPIC_API_KEY_2", "")

    results = [
        call_api("Key 1", key1),
        call_api("Key 2", key2),
    ]

    header = f"Date: {date_str}\nTime: {time_str}\nModel: {MODEL}\n"
    body = "\n\n".join(format_result(r) for r in results)
    log_content = f"{header}\n{body}\n"

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{date_str}.txt"
    with log_path.open("a", encoding="utf-8") as f:
        if log_path.stat().st_size > 0:
            f.write("\n" + "=" * 60 + "\n\n")
        f.write(log_content)

    print(log_content)

    # Exit 0 even if both fail — the log itself is the artifact we want committed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
