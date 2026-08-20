"""
prompt_engine.py

Core logic for the Prompt Engineering Assistant.

Two responsibilities live here, matching the two resume bullets this
project is built around:

1. generate_prompt(...)   -> assembles a structured prompt from a task
   type, context, constraints, and a desired output format.
2. evaluate_prompt(...)   -> scores a set of prompt inputs on clarity,
   specificity, and completeness, and returns concrete suggestions
   for refining it further.

The module has zero web-framework dependencies so it can be unit
tested (see tests/test_prompt_engine.py) or reused from a CLI, a
notebook, or a different front end entirely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


# ---------------------------------------------------------------------------
# Task templates
# ---------------------------------------------------------------------------
# Each task type gets a short "role" framing and a set of default
# section labels. Keeping these as data (not hardcoded strings deep in
# a function) makes it easy to add a new task type later.

TASK_TEMPLATES: Dict[str, Dict[str, str]] = {
    "coding": {
        "role": (
            "You are an experienced software engineer who writes clean, "
            "well-documented, production-quality code."
        ),
        "task_label": "Coding Task",
        "default_format": (
            "Return the final code in a single fenced code block, followed by "
            "a short bullet list explaining any non-obvious decisions."
        ),
    },
    "analysis": {
        "role": (
            "You are a careful analyst who reasons from evidence, states "
            "assumptions explicitly, and avoids overclaiming."
        ),
        "task_label": "Analysis Task",
        "default_format": (
            "Return a short summary (2-3 sentences), then supporting points "
            "as bullets, then a final 'Confidence & caveats' section."
        ),
    },
    "content-generation": {
        "role": (
            "You are a skilled writer who adapts tone and structure to the "
            "audience and purpose described below."
        ),
        "task_label": "Content Generation Task",
        "default_format": (
            "Return the finished piece only, formatted for direct publishing "
            "(no meta-commentary before or after)."
        ),
    },
}

VAGUE_WORDS = {
    "somehow", "stuff", "things", "maybe", "kind of", "sort of",
    "etc", "whatever", "good", "nice", "better", "asap",
}


@dataclass
class PromptInputs:
    """Everything the user supplies to build one prompt."""
    task_type: str
    goal: str
    context: str = ""
    constraints: List[str] = field(default_factory=list)
    output_format: str = ""


def generate_prompt(inputs: PromptInputs) -> str:
    """Assemble a structured prompt from the user's inputs.

    The output always has four sections — Role, Context, Task,
    Constraints, Output Format — so the resulting prompt is
    consistent regardless of task type, which is what makes it easier
    to evaluate and refine (see evaluate_prompt below).
    """
    template = TASK_TEMPLATES.get(inputs.task_type, TASK_TEMPLATES["analysis"])

    lines: List[str] = []
    lines.append(f"### Role")
    lines.append(template["role"])
    lines.append("")

    if inputs.context.strip():
        lines.append(f"### Context")
        lines.append(inputs.context.strip())
        lines.append("")

    lines.append(f"### {template['task_label']}")
    lines.append(inputs.goal.strip())
    lines.append("")

    if inputs.constraints:
        lines.append("### Constraints")
        for c in inputs.constraints:
            c = c.strip()
            if c:
                lines.append(f"- {c}")
        lines.append("")

    lines.append("### Output Format")
    lines.append(inputs.output_format.strip() or template["default_format"])

    return "\n".join(lines).strip() + "\n"


# ---------------------------------------------------------------------------
# Evaluation / refinement
# ---------------------------------------------------------------------------

def evaluate_prompt(inputs: PromptInputs) -> Dict:
    """Score the prompt inputs and return actionable suggestions.

    This is a deliberately transparent, rule-based scorer (no external
    API calls) so the project runs standalone and the scoring logic is
    easy to explain in an interview: every point gained or lost maps
    to one readable rule below.
    """
    score = 0
    max_score = 100
    suggestions: List[str] = []

    # Goal clarity (30 pts)
    goal = inputs.goal.strip()
    if len(goal) >= 20:
        score += 20
    else:
        suggestions.append(
            "Your task description is quite short — add a sentence or two "
            "about exactly what a good result looks like."
        )
    if goal and goal[0].isupper():
        score += 5
    if goal.endswith((".", "!", "?")):
        score += 5

    # Context (25 pts)
    if inputs.context.strip():
        score += 15
        if len(inputs.context.strip()) >= 40:
            score += 10
        else:
            suggestions.append(
                "Consider adding more background in Context — who the "
                "output is for, or what has already been tried."
            )
    else:
        suggestions.append(
            "No context provided. A sentence of background (audience, "
            "prior attempts, constraints of the environment) usually "
            "improves relevance a lot."
        )

    # Constraints (20 pts)
    real_constraints = [c for c in inputs.constraints if c.strip()]
    if real_constraints:
        score += min(20, 7 * len(real_constraints))
    else:
        suggestions.append(
            "No constraints listed. Even one or two (length, tone, "
            "language/framework, things to avoid) sharply narrows the "
            "space of acceptable answers."
        )

    # Output format (15 pts)
    if inputs.output_format.strip():
        score += 15
    else:
        suggestions.append(
            "No output format specified — the assistant will fall back to "
            "a sensible default, but specifying one yourself (e.g. table, "
            "JSON schema, numbered steps) improves consistency run-to-run."
        )

    # Vague language penalty (up to -15)
    combined_text = " ".join([goal, inputs.context] + real_constraints).lower()
    hits = [w for w in VAGUE_WORDS if w in combined_text]
    if hits:
        penalty = min(15, 5 * len(hits))
        score -= penalty
        suggestions.append(
            "Vague wording detected (" + ", ".join(sorted(hits)) +
            "). Swap these for concrete, measurable language."
        )

    # Length sanity bonus (10 pts) — not too short, not a wall of text
    total_len = len(combined_text)
    if 40 <= total_len <= 1200:
        score += 10

    score = max(0, min(max_score, score))

    if score >= 85:
        verdict = "Strong — this prompt is specific and well-structured."
    elif score >= 60:
        verdict = "Workable — a few refinements will improve consistency."
    else:
        verdict = "Needs work — the model will have to guess at a lot here."

    return {
        "score": score,
        "verdict": verdict,
        "suggestions": suggestions,
    }
