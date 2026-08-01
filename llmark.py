from typing import Callable

from .evaluator.evaluators import _Evaluator
from .evaluator.plugin import Plugin

class LLMark:
    def __init__(self, func: Callable[[str], str], base_path: str = ".", ext_plugins: dict[str, Plugin] = {}):
        self._eval = _Evaluator(base_path, ext_plugins)
        self._chat_func = func

    def _run_test(self, test: dict[str, any]) -> dict[str, any]:
        if "type" not in test or "question" not in test or "options" not in test:
            raise ValueError('Test must contain "type", "question" and "options".')

        type: str = str(test["type"])
        question: str = str(test["question"])
        options: dict[str, str] = test["options"]

        if not isinstance(options, dict):
            raise ValueError('"options" must be a dictionary mapping.')

        prompt = self._eval._format_prompt(type, options, question)

        resp = self._chat_func(prompt)

        return self._eval._evaluate(type, options, resp)

    def run_test_set(self, test_set: dict[str, any]) -> dict[str, any]:
        if "evaluators" not in test_set or "questions" not in test_set:
            raise ValueError('Test set must contain "evaluators" and "questions".')

        evaluators: dict[str, str] = test_set["evaluators"]
        questions: list[any] = test_set["questions"]

        if not isinstance(evaluators, dict):
            raise ValueError('"evaluators" must be a dictionary mapping.')

        if not isinstance(questions, list):
            raise ValueError('"questions" must be a list.')

        self._eval._load_evaluators(evaluators)

        results: list[any] = []
        score_collector: int = 0
        score_counter: int = 0

        total = len(questions)

        for idx, question in enumerate(questions, start=1):
            print(f"Running test {idx}/{total}")

            result = self._run_test(question)

            result["question"] = question
            results.append(result)

            score_collector = score_collector + int(result["score"])
            score_counter = score_counter + 1

        self._eval._unload_evaluators()

        average_score = score_collector / score_counter

        return {"average_score": average_score, "results": results}