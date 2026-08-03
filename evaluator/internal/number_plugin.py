import math
from llmark.evaluator.plugin import Plugin


class _NumberPlugin(Plugin):
    """
    This plugin checks a model's numeric answer against an expected value.
    It supports integers, floats, and optional tolerance for floating‑point
    comparisons.

    Expected options dict:
    - "value"      : the correct number (int or float)
    - "tolerance"  : optional absolute tolerance for floats (default = 0.0) If omitted the comparison is exact.
    """

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def format_prompt(self, options: dict[str, any], question: str) -> str:
        """
        Append a short hint about the expected numeric type.
        The evaluator itself does not enforce a specific format; it only
        parses whatever the model returns as a number.
        """

        hint = "Provide the answer as a plain number (integer or decimal)."
        return f"{question}\n\n{hint}"

    def evaluate(self, options: dict[str, any], response: str) -> dict[str, any]:
        """
        Compare the numeric response to the expected value.

        Returns:
            {"score": 100, "reason": ""} on success,
            {"score": 0, "reason": "<explanation>"} on failure.
        """

        if "value" not in options:
            raise ValueError('Option "value" (expected number) is required.')

        expected = options["value"]
        tolerance = float(options.get("tolerance", 0.0))

        try:
            # Convert the model's raw response to a Python number.
            # Accept both integer‑like strings ("42") and float‑like strings
            # ("3.14", "2e-3").
            resp_num = float(response.strip())
            # If the expected value is an int and the parsed float has no
            # fractional part, treat it as an int for exact comparison.
            if isinstance(expected, int) and resp_num.is_integer():
                resp_num = int(resp_num)
        except ValueError:
            return {
                "score": 0,
                "reason": f"Response could not be parsed as a number: \"{response}\"",
            }

        if isinstance(expected, (int, float)):
            diff = abs(resp_num - expected)
            if diff <= tolerance:
                return {"score": 100, "reason": ""}
            else:
                reason = (
                    f"Expected {expected}"
                    + (f" ±{tolerance}" if tolerance > 0 else "")
                    + f", got {resp_num} (difference {diff})"
                )
                return {"score": 0, "reason": reason}
        else:
            return {
                "score": 0,
                "reason": f"Invalid expected value type: {type(expected)}",
            }