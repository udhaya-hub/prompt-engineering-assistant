"""
app.py

Flask front end for the Prompt Engineering Assistant.

Routes:
    GET  /            -> the form + live preview page
    POST /api/generate -> {task_type, goal, context, constraints, output_format}
                           => {"prompt": "..."}
    POST /api/evaluate -> same body
                           => {"score": int, "verdict": str, "suggestions": [...]}

Run locally:
    pip install -r requirements.txt
    python app.py
    # then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify

from prompt_engine import PromptInputs, generate_prompt, evaluate_prompt, TASK_TEMPLATES

app = Flask(__name__)


def _inputs_from_request() -> PromptInputs:
    data = request.get_json(silent=True) or request.form
    constraints_raw = data.get("constraints", "")
    if isinstance(constraints_raw, list):
        constraints = constraints_raw
    else:
        constraints = [c for c in constraints_raw.split("\n")]

    return PromptInputs(
        task_type=data.get("task_type", "analysis"),
        goal=data.get("goal", ""),
        context=data.get("context", ""),
        constraints=constraints,
        output_format=data.get("output_format", ""),
    )


@app.route("/")
def index():
    return render_template("index.html", task_types=TASK_TEMPLATES.keys())


@app.route("/api/generate", methods=["POST"])
def api_generate():
    inputs = _inputs_from_request()
    prompt = generate_prompt(inputs)
    return jsonify({"prompt": prompt})


@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    inputs = _inputs_from_request()
    result = evaluate_prompt(inputs)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
