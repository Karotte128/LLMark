from typing import Any, Dict, List
import re
from ..plugin import Plugin

def _norm(text: str, case_sensitive: bool) -> str:
    """Normalise text for comparison."""
    return text if case_sensitive else text.lower()


def _as_word_boundary_pattern(word: str) -> str:
    """
    Return a regex pattern that matches *word* as a whole word.
    The pattern is safe for simple words without special regex chars;
    they are escaped automatically.
    """
    import re

    return r"\b" + re.escape(word) + r"\b"


class _StringMatchPlugin(Plugin):
    """
    Flexible string comparison plugin for LLM test suites.
    The evaluator checks a response against one or more target strings using a selectable matching mode.

    Supported modes (passed via the ``mode`` key in *options*):
        * equals
        * contains
        * contains_not
        * starts_with
        * ends_with

    Required option keys:
        - ``mode``: one of the modes listed in the module docstring.
        - ``targets`` (or ``target`` for single value modes): string(s) to check.

    Additional option keys (optional):
        - ``case_sensitive`` (bool, default False).
        - ``word_based`` (bool, default True) – only used with modes ``contains`` and ``contains_not``. When true, a target is matched as a whole word instead of a substring.

    The plugin raises ``ValueError`` for missing or malformed options.
    """

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def format_prompt(self, _: Dict[str, Any], question: str) -> str:
        return (
            f"{question}\n\n"
            "Provide the answer as plain text. Do not include any explanation for your answer."
        )

    def evaluate(self, options: Dict[str, Any], response: str) -> Dict[str, Any]:
        mode = options.get("mode")
        case_sensitive = bool(options.get("case_sensitive", False))
        word_based = bool(options.get("word_based", True))

        if not isinstance(mode, str):
            raise ValueError('Option "mode" must be a string.')

        raw_targets = options.get("targets") or options.get("target")
        if isinstance(raw_targets, (list, tuple)):
            targets: List[str] = [str(t) for t in raw_targets]
        elif isinstance(raw_targets, str):
            targets = [raw_targets]
        else:
            raise ValueError('Option "target(s)" must be a string or list of strings.')

        if not targets:
            raise ValueError("At least one target string must be provided.")

        norm_resp = _norm(response.strip(), case_sensitive)
        norm_tgts = [_norm(t, case_sensitive) for t in targets]

        try:
            if mode == "equals":
                result = norm_resp in norm_tgts

            elif mode == "contains":
                if word_based:
                    patterns = [_as_word_boundary_pattern(t) for t in norm_tgts]
                    result = any(re.search(p, norm_resp) for p in patterns)
                else:
                    result = any(t in norm_resp for t in norm_tgts)

            elif mode == "contains_not":
                if word_based:
                    patterns = [_as_word_boundary_pattern(t) for t in norm_tgts]
                    result = all(not re.search(p, norm_resp) for p in patterns)
                else:
                    result = all(t not in norm_resp for t in norm_tgts)

            elif mode == "starts_with":
                result = any(norm_resp.startswith(t) for t in norm_tgts)

            elif mode == "ends_with":
                result = any(norm_resp.endswith(t) for t in norm_tgts)

            else:
                raise ValueError(f'Unsupported mode "{mode}".')
        except IndexError:
            raise ValueError(
                "At least one target string must be provided for the selected mode."
            )

        if result:
            return {"score": 100, "reason": "", "response": response}
        else:
            expected_desc = f"mode={mode}, target{'s' if len(targets) > 1 else ''}={targets}"
            if word_based and mode == "contains":
                expected_desc += ", word_based=True"
            return {
                "score": 0,
                "reason": f'String check failed – {expected_desc}. Got: "{response}"',
                "response": response,
            }