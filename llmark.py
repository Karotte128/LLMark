from typing import Callable

from .evaluator.evaluators import _Evaluator
from .evaluator.plugin import Plugin

class LLMark:
    """
    Core orchestrator for running an LLM benchmark.

    Parameters
    ----------
    func : Callable[[str], str]
        A callable that receives a formatted prompt and returns the raw model
        response.  This is where you hook your own API / client.
    base_path : str, optional
        Directory from which file-based plugins are resolved (default ``"."``).
    ext_plugins : dict[str, Plugin], optional
        Mapping of *external* plugin names to already instantiated ``Plugin``
        objects.

    The class holds a private :class:`_Evaluator` instance that manages loading,
    formatting and evaluating each question.
    """

    def __init__(self, func: Callable[[str], str], base_path: str = ".", ext_plugins: dict[str, Plugin] = {}):
        self._eval = _Evaluator(base_path, ext_plugins)
        self._chat_func = func

    def _run_test(self, test: dict[str, any]) -> dict[str, any]:
        """
        Validate a single test description, format the prompt, call the model,
        and evaluate the response.

        The *test* dict must contain ``type``, ``question`` and ``options``.
        Raises
        ------
        ValueError
        If required keys are missing or ``options`` is not a mapping.
        """
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
        """
        Run an entire benchmark.

        The *test_set* must contain:
        * ``evaluators`` – a mapping of evaluator specifications to aliases.
        * ``questions``   – a list of question objects as described in the
            README.

        Returns
        -------
        dict
            {
                "average_score": float,
                "results": [
                    {"question": <original>, "score": int, "reason": str}, …
                ]
            }

        Notes
        -----
        * All evaluators are loaded, each question is processed (progress printed),
        then the evaluators are unloaded.
        * ``average_score`` is computed as the arithmetic mean of all integer scores.
        """

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