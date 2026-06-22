from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def _get_system_prompt(tier: str) -> str:
    if tier == "safe":
        return (
            "You are a home repair assistant answering a safe question. This repair is low-risk "
            "and appropriate for a typical homeowner, so provide a clear, practical answer "
            "with tools, materials, and step-by-step guidance. Keep the response specific "
            "and actionable, use simple language, and include any basic safety checks the user "
            "should do before starting. Do not add a professional referral for this safe tier."
        )
    if tier == "caution":
        return (
            "You are a home repair assistant answering a caution-tier question. Begin by saying "
            "this repair is doable for a careful homeowner, but it carries real risk and hiring "
            "a licensed professional is recommended if the user is unsure. Then offer practical "
            "advice with clear safety warnings, call out the main hazards, and recommend turning "
            "off power or water as needed. Keep the advice balanced: specific enough to help, "
            "but with an explicit recommendation for professional help up front."
        )
    if tier == "refuse":
        return (
            "You are a home repair assistant answering a refuse-tier question. Do not provide any steps, "
            "procedures, or instructions — not even general guidance or a sequence of actions. Do not "
            "describe how to do the repair. Instead, explain why this work is dangerous or inappropriate "
            "for a homeowner, mention the key risks such as fire, flooding, structural damage, or injury, "
            "and clearly tell the user to hire a licensed professional or contact their local building authority. "
            "Keep the response useful by naming the kind of contractor who handles this work and what the user "
            "should tell that professional, but do not include DIY instructions."
        )
    # Fallback for unknown tier: use caution-style behavior
    return (
        "You are a home repair assistant answering a question with uncertain tier. Explain that the repair "
        "may involve risk, recommend a licensed professional if the user is unsure, and keep the advice "
        "focused on safety checks rather than confident DIY instructions. This ensures the response errs on "
        "the side of caution while the classifier is still being developed."
    )


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.

    `tier` is one of "safe", "caution", or "refuse". If an unknown tier is received,
    this function treats it like caution so the system fails safe.
    """
    normalized_tier = tier.lower() if isinstance(tier, str) else "unknown"
    if normalized_tier not in {"safe", "caution", "refuse"}:
        normalized_tier = "caution"

    system_prompt = _get_system_prompt(normalized_tier)
    user_prompt = f"Question: {question}\nAnswer the question according to the system prompt."

    try:
        resp = _client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=LLM_MODEL,
            temperature=0.0,
        )
        if not resp or not getattr(resp, "choices", None):
            return "Sorry, I couldn't create a response right now. Please try again later."

        answer = resp.choices[0].message.content or ""
        return answer.strip()
    except Exception:
        return "Sorry, I couldn't generate a response right now; please try again later."
