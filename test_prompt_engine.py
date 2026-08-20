import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_engine import PromptInputs, generate_prompt, evaluate_prompt


def make_inputs(**overrides):
    defaults = dict(
        task_type="coding",
        goal="Write a function that validates email addresses.",
        context="Used in a Flask signup form; must not raise on bad input.",
        constraints=["Python 3.11+", "No third-party libraries", "Under 30 lines"],
        output_format="A single fenced code block.",
    )
    defaults.update(overrides)
    return PromptInputs(**defaults)


def test_generate_prompt_includes_all_sections():
    prompt = generate_prompt(make_inputs())
    assert "### Role" in prompt
    assert "### Context" in prompt
    assert "### Coding Task" in prompt
    assert "### Constraints" in prompt
    assert "### Output Format" in prompt
    assert "Python 3.11+" in prompt


def test_generate_prompt_falls_back_to_default_format():
    inputs = make_inputs(output_format="")
    prompt = generate_prompt(inputs)
    assert "fenced code block" in prompt  # default for "coding"


def test_generate_prompt_omits_empty_context():
    inputs = make_inputs(context="")
    prompt = generate_prompt(inputs)
    assert "### Context" not in prompt


def test_evaluate_prompt_scores_a_complete_prompt_highly():
    result = evaluate_prompt(make_inputs())
    assert result["score"] >= 60
    assert "verdict" in result


def test_evaluate_prompt_flags_missing_context_and_constraints():
    inputs = make_inputs(context="", constraints=[], output_format="")
    result = evaluate_prompt(inputs)
    assert result["score"] < 60
    joined = " ".join(result["suggestions"])
    assert "context" in joined.lower()
    assert "constraint" in joined.lower()


def test_evaluate_prompt_penalizes_vague_language():
    inputs = make_inputs(goal="Do something good with the stuff, maybe.")
    result = evaluate_prompt(inputs)
    joined = " ".join(result["suggestions"]).lower()
    assert "vague" in joined


def test_evaluate_prompt_score_is_bounded():
    inputs = make_inputs(
        goal="x",
        context="",
        constraints=[],
        output_format="",
    )
    result = evaluate_prompt(inputs)
    assert 0 <= result["score"] <= 100


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
