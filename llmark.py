from typing import Callable

from .evaluator.evaluators import Evaluator
from .evaluator.plugin import Plugin

class LLMark:
    def __init__(self, ext_plugins: dict[str, Plugin], func: Callable[[str], str]):
        self._eval = Evaluator(ext_plugins)
        self._chat_func = func

    def run_test(self, test: dict[str, any]) -> dict[str, any]:
        if "type" not in test or "question" not in test or "options" not in test:
            raise ValueError('Test must contain "type", "question" and "options".')

        type: str = str(test["type"])
        question: str = str(test["question"])
        options: dict[str, str] = test["options"]

        if not isinstance(options, dict):
            raise ValueError('"options" must be a dictionary mapping.')

        prompt = self._eval.format_prompt(type, options, question)

        resp = self._chat_func(prompt)

        return self._eval.evaluate(type, options, resp)

    def load_evaluators(self, eval_sources: dict[str, str]) -> None:
        self._eval.load_evaluators(eval_sources)

    def unload_evaluators(self) -> None:
        self._eval.unload_evaluators()