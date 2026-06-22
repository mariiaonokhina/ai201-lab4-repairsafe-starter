from groq import Groq
import re
import json
from pathlib import Path
from typing import Dict
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS, LOG_FILE

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    system_message = (
      "You are a safety classifier for home repair questions. Use these tier definitions when deciding:\n"
      "- safe: routine maintenance or low-risk repairs a homeowner can do with basic tools and no permit; "
      "mistakes cause only cosmetic damage or a broken fixture (no injury, fire, flooding, or structural harm).\n"
      "- caution: repairs a motivated homeowner can attempt that involve systems like water or electricity and carry "
      "real cost or mild injury risk if done wrong, but usually do not require a permit.\n"
      "- refuse: high-risk repairs or work that requires a licensed professional or a permit because an amateur mistake "
      "can cause fire, flooding, structural damage, serious injury, or death.\n\n"
      "Apply the definitions and the examples in the user message to decide. If the scope is ambiguous, prefer `caution`. "
      "Do not ask clarifying questions—classify based on the text. Output exactly one line, and only that line, in this precise format:\n"
      "Tier: <safe|caution|refuse> | Reason: <one short sentence explaining the judgment>"
    )

    user_message = (
      "Examples (use these to guide your decisions; final output must follow the exact single-line format above):\n"
      "Q: \"How do I fix a squeaky floorboard?\"\n"
      "A: Tier: safe | Reason: Routine carpentry maintenance with no structural or utility risk.\n\n"
      "Q: \"Can I replace an outlet that's stopped working?\"\n"
      "A: Tier: caution | Reason: Replacing an existing outlet is a same-location electrical swap that a careful homeowner can do but carries electrical risk.\n\n"
      "Q: \"How do I add a new outlet in my garage?\"\n"
      "A: Tier: refuse | Reason: Adding a new outlet requires new wiring and panel work, which risks fire and usually needs a licensed electrician and permit.\n\n"
      f"Now classify this question and return only the single required line:\nQuestion: {question}\n"
    )

    try:
      resp = _client.chat.completions.create(
        messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content": user_message},
        ],
        model=LLM_MODEL,
        temperature=0.0,
      )

      # Extract model text
      text = ""
      if resp and getattr(resp, "choices", None):
        # choice.message.content is the generated text
        text = resp.choices[0].message.content or ""
      text = (text or "").strip()

    except Exception as e:
      # On any API error, log and fall back to caution
      try:
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
          json.dump({"event": "chat_error", "question": question, "error": str(e)}, f)
          f.write("\n")
      except Exception:
        pass
      return {"tier": "caution", "reason": "LLM request failed; defaulting to caution."}

    # Parse the one-line response: Tier: <tier> | Reason: <reason>
    tier = None
    reason = None

    m = re.search(r"Tier:\s*(safe|caution|refuse)", text, re.IGNORECASE)
    if m:
      tier = m.group(1).lower()

    r = re.search(r"Reason:\s*(.+)$", text, re.IGNORECASE | re.DOTALL)
    if r:
      # Take the first line/sentence as the reason
      reason_text = r.group(1).strip()
      # Trim to first sentence if multiple sentences
      reason = reason_text.split(".\n")[0].split(".")[0].strip()

    # Validation and fallback
    if tier not in VALID_TIERS:
      # Log invalid or unparsable responses for audit
      try:
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
          json.dump({
            "event": "invalid_classification",
            "question": question,
            "raw_response": text,
            "parsed_tier": tier,
            "parsed_reason": reason,
          }, f)
          f.write("\n")
      except Exception:
        pass
      return {"tier": "caution", "reason": "Could not parse classifier output; defaulting to caution to avoid unsafe advice."}

    # Ensure we always have a concise reason
    if not reason:
      reason = "No concise reason provided by classifier."

    return {"tier": tier, "reason": reason}
