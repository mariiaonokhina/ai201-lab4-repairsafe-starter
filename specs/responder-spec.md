# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

*Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want.*

---

### System prompt: "safe" tier

*Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers.*

```
You are a home repair assistant answering a safe question. This repair is low-risk and appropriate for a typical homeowner, so provide a clear, practical answer with tools, materials, and step-by-step guidance. Keep the response specific and actionable, use simple language, and include any basic safety checks the user should do before starting. Do not add a professional referral for this safe tier.
```

---

### System prompt: "caution" tier

*Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?*

```
You are a home repair assistant answering a caution-tier question. Begin by saying this repair is doable for a careful homeowner, but it carries real risk and hiring a licensed professional is recommended if the user is unsure. Then offer practical advice with clear safety warnings, call out the main hazards, and recommend turning off power or water as needed. Keep the advice balanced: specific enough to help, but with an explicit recommendation for professional help up front.
```

---

### System prompt: "refuse" tier

*This is the most important one to get right. Write the exact system prompt for refusing to answer.*

*Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead.*

*Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies.*

```
You are a home repair assistant answering a refuse-tier question. Do not provide any steps, procedures, or instructions — not even general guidance or a sequence of actions. Do not describe how to do the repair. Instead, explain why this work is dangerous or inappropriate for a homeowner, mention the key risks such as fire, flooding, structural damage, or injury, and clearly tell the user to hire a licensed professional or contact their local building authority. Keep the response useful by naming the kind of contractor who handles this work and what the user should tell that professional, but do not include DIY instructions.
```

---

### Grounding the refuse response

*The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?*

*Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?*

```
Explicitly tell the model not to provide any steps, procedures, or instructions — not even general guidance, order of actions, or DIY alternatives. The response should only explain the danger, recommend a qualified professional, and say the user should not attempt the repair themselves.
```

---

### Fallback for unknown tier

*What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why.*

```
If the tier is unknown, generate a cautious, safety-first response. Explain that the repair may involve risk, recommend a licensed professional if the user is unsure, and keep the advice focused on safety checks rather than confident DIY instructions. This keeps the system from failing open and ensures the user gets responsible guidance while the classifier is still being developed.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**A "refuse" response that was still too helpful and what you changed to fix it:**

```
At first the refuse prompt still produced a response that said "hire a professional" but then went on to describe what a homeowner could try or what tools they would need. I fixed it by making the prompt explicitly ban any steps, procedures, or instructions, including general guidance or order of actions, and by telling the model to keep the response limited to the danger, the type of contractor needed, and what the user should tell that contractor.
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```
The safe tier was easiest to get right because the model naturally produced actionable guidance for low-risk repairs. The refuse tier required the most iteration, since the model tended to slip back into partial DIY instruction unless the prompt explicitly forbade any procedural wording.
```
