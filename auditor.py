import json
import os
from datetime import datetime, timezone
from config import LOG_FILE


def log_interaction(question: str, tier: str, response: str) -> None:
    """
    Append a structured record of this interaction to the audit log.

    Each record is a single JSON object written as one line to LOG_FILE.
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    clean_question = question.replace("\n", " ").replace("\r", " ").strip()
    clean_response = response.replace("\n", " ").replace("\r", " ").strip()
    truncated_question = clean_question[:300]
    response_preview = clean_response[:200]

    log_record = {
        "timestamp": timestamp,
        "tier": tier,
        "question": truncated_question,
        "response_preview": response_preview,
        "question_length": len(question),
        "response_length": len(response),
    }

    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump(log_record, f, ensure_ascii=False)
        f.write("\n")

    question_display = json.dumps(truncated_question, ensure_ascii=False)
    preview_display = json.dumps(response_preview, ensure_ascii=False)
    print(
        f"LOGGED tier={tier} | question={question_display} | response_preview={preview_display}"
    )
