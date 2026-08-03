# LLMark – LLM Benchmarking Tool

LLMark is a lightweight Python framework for evaluating Large Language Models (LLMs) against custom test suites.  
A test suite is simply a JSON file that describes one or more questions, the type of evaluation to run, and the expected answer(s).

## Table of Contents
1. [Installation](#installation)  
2. [Quick‑Start Example](#quick-start-example)  
3. [Test File Format](#test-file-format)  
4. [Running a Benchmark](#running-a-benchmark)  
5. [Creating Your Own Plugins](#creating-your-own-plugins)  
6. [API Reference (Python)](#api-reference-python)  
7. [Acknowledgements](#acknowledgements)

---

### Installation

```bash
# Clone the repository
git clone https://github.com/your‑username/LLMark.git
cd LLMark
```

> **Note:** The core of LLMark relies solely on the Python standard library, so no additional runtime dependencies are required.

---

### Quick‑Start Example

1. Save a test suite (see the *Test File Format* section) as `sample_test.json`.  
2. Run the benchmark with a simple wrapper that forwards prompts to your LLM:

```python
import json
from llmark import LLMark

# ----------------------------------------------------------------------
# Replace this function with whatever API you use to talk to your model.
# It must accept a string prompt and return the model's raw response.
# ----------------------------------------------------------------------
def chat(prompt: str) -> str:
    # Example stub – replace with real call
    return "a" # dummy answer for demonstration

# Load test suite
with open("sample_test.json", "r") as f:
    test_set = json.load(f)

# Initialise LLMark
benchmark = LLMark(chat) # base_path defaults to "." (current dir), no external plugins provided

# Run the test set and print a summary
result = benchmark.run_test_set(test_set)
print(f"Average score: {result['average_score']:.2f}")
for r in result["results"]:
    print(r["question"]["id"], "→", r["score"])
```

Running the script prints something like:

```
Running test 1/2
Running test 2/2
Average score: 100.00
test-01 → 100
test-02 → 100
```

---

### Test File Format

A benchmark is a JSON object with two top‑level keys:

| Key | Description |
|-----|-------------|
| `evaluators` | Mapping of *evaluator spec* → *alias*. The spec can be **internal** (bundled), **file** (custom plugin, loaded at runtime) or **external** (provided by the project). Example: `"internal:multiple-choice": "mcq"` |
| `questions`  | List of question objects. Each object must contain:<br>`type` – the evaluator alias to use (e.g., `"mcq"`).<br>`question` – the prompt that will be sent to the model.<br>`options` – a dictionary whose content depends on the evaluator type. For the built‑in *multiple‑choice* evaluator you need `choices` (a dict of label → text) and `answer` (the correct label). |

**List of available evaluators::
- "internal:multiple-choice"
- "internal:string"
- "internal:number"
- "internal:regex"

**Example (`sample_test.json`)**

```json
{
  "evaluators": {
    "internal:string": "str"
  },
  "questions": [
    {
      "type": "str",
      "id": "str-01",
      "question": "What is the capital of France?",
      "options": {
        "mode": "equals",
        "target": "Paris",
        "case_sensitive": false
      }
    }
  ]
}
```


The file `reference.json` contains a reference of all internal plugins.

---

### Running a Benchmark

The core class is `llmark.llmark.LLMark`. Its workflow is:

1. **Prompt formatting** – the selected evaluator formats the prompt (`format_prompt`).  
2. **Model call** – your callback receives the formatted prompt and returns a raw string response.  
3. **Scoring** – the evaluator checks the answer (`evaluate`) and returns a numeric score (0 or 100 for MCQ).  

```python
benchmark = LLMark(chat_function)
results = benchmark.run_test_set(test_set)   # ← runs every question
```

The return value is a dict:

```json
{
  "average_score": <float>,
  "results": [
    {
      "question": { …original question object… },
      "score": <int>,                // e.g. 0 or 100 for MCQ
      "reason": "<optional explanation>"
    },
    …
  ]
}
```

---

### Creating Your Own Plugins

LLMark is plugin‑driven. A **plugin** must inherit from `llmark.Plugin` and implement four abstract methods:

| Method | Purpose |
|--------|---------|
| `load(self)`   | Initialise external resources (e.g., open a DB connection). |
| `unload(self)` | Clean up resources when the benchmark finishes. |
| `format_prompt(self, options, question) -> str` | Turn the raw question + options into the exact prompt you want to send to the model. |
| `evaluate(self, options, response) -> dict` | Return a dictionary with `"score"` (0‑100) and optional `"reason"` describing why the answer was wrong/right. |

**Registering a plugin**

* **External plugin:** Add it to your codebase and pass it to LLMark:
```python
import json
from llmark import LLMark

# import MyPlugin
from my_plugin import MyPlugin

# give it a name, this will later be your evaluator string (e.g. "external:my_plugin")
ext_plugins = {
    "my_plugin": MyPlugin()
}

llmark = LLMark(chat, ".", ext_plugins) # pass it to LLMark
```

* **File‑based plugin:** Place a Python file somewhere on disk, make sure it defines a class named `Plugin` (or subclass of the base), then reference it in your test suite as `"file:/path/to/my_plugin.py": "myalias"`.

**Example – simple “yes/no” evaluator**

```python
# my_yesno.py
from llmark import Plugin

class YesNoPlugin(Plugin):
    def load(self): pass
    def unload(self): pass

    def format_prompt(self, options, question):
        return f"{question} (answer with \"yes\" or \"no\")"

    def evaluate(self, options, response):
        expected = options["answer"].strip().lower()
        got = response.strip().lower()
        score = 100 if got == expected else 0
        reason = "" if score == 100 else f"Expected {expected}, got {got}"
        return {"score": score, "reason": reason}
```

Add it to a test file:

```json
{
  "evaluators": {
    "file:my_yesno.py": "yn"
  },
  …
}
```

---

### API Reference (Python)

| Module / Class | Key Methods / Attributes | Description |
|----------------|--------------------------|-------------|
| `llmark.LLMark` | `__init__(func, base_path='.', ext_plugins={})`<br>`run_test_set(test_set)` | Core orchestrator. Holds an `Evaluator` instance and forwards prompts to the user‑supplied `func`. |
| `llmark.Plugin` | Abstract base class with `load`, `unload`, `format_prompt`, `evaluate` | All evaluator plugins must inherit from this class. |

All public classes and functions already contain inline docstrings; you can view them with `help()` or by reading the source files.


---

#### Acknowledgements

The core of LLMark (`LLMark` class, plugin manager, built‑in evaluators) was written by the original repository author (Karotte128) and is documented in the source code.
This project is released under the MIT License.