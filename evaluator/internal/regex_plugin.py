import re
from typing import Any, Dict

from llmark.evaluator.plugin import Plugin

class _RegexPlugin(Plugin):
    """
    Regular Expression Evaluator Plugin

    Options expected in the test definition:
    - "regex"  : a Python compatible regular expression string.
        The response is considered a match if ``re.search`` finds any
        occurrence of this pattern.
    - "invert" : optional bool (default: False). When True the result is
        inverted – i.e. a *non-match* yields a passing score.
    """

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def format_prompt(self, _: Dict[str, Any], question: str) -> str:
        return question #Use the unmodified question

    def evaluate(self, options: Dict[str, Any], response: str) -> Dict[str, Any]:
        if "regex" not in options:
            raise ValueError('Option "regex" is required for the regex evaluator.')

        pattern = str(options["regex"])
        invert = bool(options.get("invert", False))

        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            raise ValueError(f'Invalid regular expression "{pattern}": {exc}') from exc

        match = compiled.search(response) is not None

        passed = not match if invert else match

        if passed:
            return {"score": 100, "reason": "", "response": response}
        else:
            reason = (
                f'Pattern {"did NOT match" if not invert else "matched"} '
                f'the response. regex="{pattern}"'
            )
            return {"score": 0, "reason": reason, "response": response}