# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine maintenance or low-risk repairs that most homeowners can do with basic tools and no permit, where mistakes lead to only cosmetic damage or a broken fixture rather than injury, fire, flooding, or structural harm.
```

**caution:**
```
Repairs a motivated homeowner can attempt with care that involve systems like water or electricity and carry real cost or mild injury risk if done wrong, but usually do not require a permit.
```

**refuse:**
```
High-risk repairs that should be handled by a licensed professional or require a permit because an amateur mistake can cause fire, flooding, structural damage, serious injury, or death.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
The best approach is to give the LLM clear tier definitions plus a few strong examples, and ask it to reason before it labels the question. That way the model has both the rules and concrete behavior to anchor its decisions. It also forces the model to weigh the risk factors instead of guessing. For ambiguous edge cases, this combination is most reliable because it makes the “why” explicit. In practice, that helps avoid mistakes like treating “replace an outlet” as refuse or “add new wiring” as safe.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
I’ll ask the model to return exactly one line with `Tier: <safe|caution|refuse>` and `Reason: <one sentence>`. That gives me a predictable format for parsing while still letting the model explain its choice. If the response doesn’t match that pattern, I’ll treat it as a fallback and return `caution` to stay safe.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a safety classifier for home repair questions. Use these tier definitions when deciding: 
- safe: routine maintenance or low-risk repairs a homeowner can do with basic tools and no permit; mistakes cause only cosmetic damage or a broken fixture (no injury, fire, flooding, or structural harm). 
- caution: repairs a motivated homeowner can attempt that involve systems like water or electricity and carry real cost or mild injury risk if done wrong, but usually do not require a permit. 
- refuse: high-risk repairs or work that requires a licensed professional or a permit because an amateur mistake can cause fire, flooding, structural damage, serious injury, or death.

Apply the definitions and the examples in the user message to decide. If the scope is ambiguous, prefer `caution`. Do not ask clarifying questions—classify based on the text. Output exactly one line, and only that line, in this precise format:
Tier: <safe|caution|refuse> | Reason: <one short sentence explaining the judgment>
```

**User message:**
```
Examples (use these to guide your decisions; final output must follow the exact single-line format above):
Q: "How do I fix a squeaky floorboard?" 
A: Tier: safe | Reason: Routine carpentry maintenance with no structural or utility risk.

Q: "Can I replace an outlet that's stopped working?" 
A: Tier: caution | Reason: Replacing an existing outlet is a same-location electrical swap that a careful homeowner can do but carries electrical risk.

Q: "How do I add a new outlet in my garage?" 
A: Tier: refuse | Reason: Adding a new outlet requires new wiring and panel work, which risks fire and usually needs a licensed electrician and permit.

Now classify this question and return only the single required line:
Question: <INSERT_QUESTION_HERE>
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Classify as "refuse" when the work requires opening or modifying utility service, structural elements, or a permit and an amateur mistake could cause fire, flooding, structural failure, serious injury, or death; otherwise, treat risky-but-same-location or like-for-like repairs as "caution."

Example 1 — Question: "Can I replace my bathroom outlet that's loose?" — Tier: caution | Reason: swapping an existing outlet is same-location work with electrical risk but usually no new circuits or panel work, so a careful homeowner can attempt it.

Example 2 — Question: "Can I move that outlet two feet to the left?" — Tier: refuse | Reason: moving an outlet typically requires running new wiring and possibly opening walls or the panel, which creates fire and code risks and often requires a licensed electrician and permit.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
- If the LLM response can't be parsed: return `{"tier":"caution","reason":"Could not parse classifier output; defaulting to caution to avoid unsafe advice."}` and log the raw LLM response and parsing error for audit.  
- If a parsed tier is not one of `VALID_TIERS`: treat it as `"caution"`, return `{"tier":"caution","reason":"Classifier returned invalid tier; defaulting to caution."}` and log the invalid value plus the raw response.  
- Also increment a telemetry counter for unparsable/invalid outputs and (optionally) record the LLM response in an audit log for later prompt tuning.  
- Rationale: fail closed (return `"caution"`) because minimizing the risk of harm is the priority; returning `"safe"` would increase the chance of unsafe advice.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
[your answer here]
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
[your answer here]
```
