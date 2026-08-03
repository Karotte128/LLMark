from typing import Any, Dict

from llmark.evaluator.plugin import Plugin

class _BooleanPlugin(Plugin):
    """
    Boolean (true/false) Evaluator Plugin

    Options expected in the test definition:
    - "value"      : the correct answer as a Python bool (True or False)
    - "true_word"  : word that represents “true” (default: "true")
    - "false_word" : word that represents “false” (default: "false")

    The plugin is case-insensitive for both the trigger words and the model’s response.
    The prompt tells the model to answer *only* with one of the two allowed words.
    """

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def format_prompt(self, options: Dict[str, Any], question: str) -> str:
        """
        Build a prompt that forces the model to answer with one of the two allowed words.
        """
        true_word  = str(options.get("true_word", "true"))
        false_word = str(options.get("false_word", "false"))

        return f"{question} Answer only with {true_word} or {false_word}."

    def evaluate(self, options: Dict[str, Any], response: str) -> Dict[str, Any]:
        """
        Compare the model’s reply to the expected boolean value.

        Returns:
            {"score": 100, "reason": ""} on success,
            {"score": 0, "reason": "<explanation>"} otherwise.
        """

        if "value" not in options:
            raise ValueError('Option "value" (expected bool) is required.')

        expected_bool = bool(options["value"])

        true_word  = str(options.get("true_word", "true")).lower()
        false_word = str(options.get("false_word", "false")).lower()

        resp_norm = response.strip().lower()

        if resp_norm == true_word:
            answered_bool = True
        elif resp_norm == false_word:
            answered_bool = False
        else:
            return {
                "score": 0,
                "reason": (
                    f"Response did not match either expected word "
                    f"(got \"{response}\", expected \"{true_word}\" or \"{false_word}\")"
                ),
            }

        if answered_bool == expected_bool:
            return {"score": 100, "reason": ""}
        else:
            exp_word = true_word if expected_bool else false_word
            return {
                "score": 0,
                "reason": f"Expected \"{exp_word}\", but got \"{response}\"",
            }