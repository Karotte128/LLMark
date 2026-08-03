from typing import Any, Dict, List
from ..plugin import Plugin

def _norm(text: str, case_sensitive: bool) -> str:
    return text if case_sensitive else text.lower()

class _StringMatchPlugin(Plugin):
    """
    This plugin implements a flexible set of string comparison modes that can be used in a test suite to verify LLM output.
    The evaluator checks a response against one or more target strings using a selectable matching mode.

    Supported modes (passed via the “mode” key in the options dict):
    * equals            – response == target                       (exact match)
    * contains          – any(t in response for t in targets)      (substring)
    * contains_not      – all(t not in response for t in targets)  (substring)
    * starts_with       – response.startswith(target)              (substring)
    * ends_with         – response.endswith(target)                (substring)

    Required option keys:
        - ``mode``: one of the modes listed in the module docstring.
        - ``targets`` (or ``target`` for single value modes): string(s) to check.
        - ``case_sensitive`` (optional, default False).

    The plugin raises ``ValueError`` if required options are missing or malformed.
    """

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def format_prompt(self, _: Dict[str, Any], question: str) -> str:
        prompt = (
            f"{question}\n\n"
            "Provide the answer as plain text. Do not include any explanation for your answer."
        )

        return prompt

    def evaluate(self, options: Dict[str, Any], response: str) -> Dict[str, Any]:
        mode = options.get("mode")
        case_sensitive = bool(options.get("case_sensitive", False))

        if not isinstance(mode, str):
            raise ValueError('Option "mode" must be a string.')

        # Retrieve the target(s)
        raw_targets = options.get("targets") or options.get("target")
        if isinstance(raw_targets, (list, tuple)):
            targets: List[str] = [str(t) for t in raw_targets]
        elif isinstance(raw_targets, str):
            targets = [raw_targets]
        else:
            raise ValueError('Option "target(s)" must be a string or list of strings.')

        norm_resp = _norm(response.strip(), case_sensitive)
        norm_tgts = [_norm(t, case_sensitive) for t in targets]

        try:
            if mode == "equals":
                # Only the first target is considered
                result = norm_resp == norm_tgts[0]

            elif mode == "contains":
                result = any(t in norm_resp for t in norm_tgts)

            elif mode == "contains_not":
                result = all(t not in norm_resp for t in norm_tgts)

            elif mode == "starts_with":
                # Only the first target is considered
                result = norm_resp.startswith(norm_tgts[0])

            elif mode == "ends_with":
                # Only the first target is considered
                result = norm_resp.endswith(norm_tgts[0])

            else:
                raise ValueError(f'Unsupported mode "{mode}".')
        except IndexError:
            raise ValueError('At least one target string must be provided for the selected mode.')

        if result:
            return {"score": 100, "reason": "", "response": response}
        else:
            expected_desc = f"mode={mode}, target{'s' if len(targets) > 1 else ''}={targets}"
            return {
                "score": 0,
                "reason": f"String check failed – {expected_desc}. Got: \"{response}\"",
                "response": response
            }