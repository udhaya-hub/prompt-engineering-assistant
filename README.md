# Prompt Engineering Assistant

A small Python/Flask app that generates **structured prompts** from a task
type, some context, a list of constraints, and a target output format —
then scores the result and suggests concrete refinements.

It was built to turn "I write good prompts" into something concrete and
demoable: a working tool with tests, not just a claim.

## What it does

- **Generates structured prompts** for three task types — coding, analysis,
  and content generation — each with its own role framing and a sensible
  default output format if you don't specify one.
- **Evaluates and refines prompts** with a transparent, rule-based scorer
  (0–100) that checks for goal clarity, context, constraints, a defined
  output format, and vague language ("stuff", "maybe", "kind of"), then
  returns specific, actionable suggestions — no external API calls, so the
  scoring logic is fully inspectable and explainable.
- **Live preview** in the browser: fill in the form on the left, hit
  *Assemble prompt*, and watch the structured prompt and its score appear
  on the right.

## Why it's structured this way

Every generated prompt follows the same four sections — `Role`, `Context`,
Task, `Constraints`, `Output Format` — regardless of task type. Keeping the
shape consistent is what makes the prompts easier to evaluate consistently
and easier to refine: the scorer checks the same four things every time.

## Tech stack

- **Backend:** Python 3, Flask
- **Core logic:** `prompt_engine.py` — plain Python, no framework
  dependency, so it's independently unit-testable (see `tests/`)
- **Frontend:** vanilla HTML/CSS/JS (no build step, no frameworks)

## Project structure

```
prompt-engineering-assistant/
├── app.py                  # Flask routes (/,  /api/generate, /api/evaluate)
├── prompt_engine.py         # Core prompt-building + scoring logic
├── templates/
│   └── index.html           # Form + live preview UI
├── static/
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_prompt_engine.py
├── requirements.txt
└── README.md
```

## Running it locally

```bash
git clone https://github.com/<your-username>/prompt-engineering-assistant.git
cd prompt-engineering-assistant
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Running it without a computer (mobile-only / no laptop)

You don't need a laptop to run or demo this project:

- **Replit** — create a free account at replit.com, "Create Repl" →
  "Import from GitHub", paste this repo's URL. Replit installs
  `requirements.txt` and runs `python app.py` automatically, and gives you
  a live public URL you can open on your phone or share in an application.
- **PythonAnywhere** — similar idea: free tier, upload/clone the repo, run
  a Flask app straight from their web-based console.
- **GitHub Codespaces** (from the GitHub mobile web UI: repo → **Code** →
  **Codespaces** → **Create codespace**) — gives you a full VS Code +
  terminal environment in the browser, on any device.

Any of these let you run, test, and screenshot the live app entirely from
a phone browser.

## Running the tests

```bash
pip install pytest
pytest tests/ -v
```

(The tests only import `prompt_engine.py`, so they also run fine in
restricted/offline environments — no Flask server needed.)

## Example

**Input**
- Task type: `coding`
- Goal: "Write a function that validates and normalizes phone numbers
  from mixed international input."
- Context: "Part of a Django signup form; must fail gracefully on
  malformed input rather than raising."
- Constraints: `Python 3.11+`, `No third-party libraries`, `Under 40 lines`
- Output format: *(left blank — falls back to the coding default)*

**Generated prompt**
```
### Role
You are an experienced software engineer who writes clean,
well-documented, production-quality code.

### Context
Part of a Django signup form; must fail gracefully on malformed input
rather than raising.

### Coding Task
Write a function that validates and normalizes phone numbers from
mixed international input.

### Constraints
- Python 3.11+
- No third-party libraries
- Under 40 lines

### Output Format
Return the final code in a single fenced code block, followed by a
short bullet list explaining any non-obvious decisions.
```

**Evaluation:** score ~85+/100, verdict "Strong", with any remaining
suggestions listed underneath.

## Possible extensions

- Save/load prompt "recipes" per task type
- A/B comparison of two prompt variants side by side
- Optional live scoring via an LLM call, alongside the rule-based scorer
- Export history as JSON/Markdown

## License

MIT — see [LICENSE](LICENSE).
