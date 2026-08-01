from ..plugin import Plugin

def _evaluate_mcq(payload: dict[str, str], response: str) -> bool:
    """
    Evaluate a multiple-choice answer.

    Parameters
    ----------
    payload : dict
        Must contain ``"choices"`` (mapping label → text) and ``"answer"``
        (the correct label).
    response : str
        The raw model output.

    Returns
    -------
    bool
        ``True`` if the normalized response matches the correct answer,
        otherwise ``False``.

    Raises
    ------
    ValueError
        If required keys are missing or ``choices`` is not a dict.
    """

    if "choices" not in payload or "answer" not in payload:
        raise ValueError('Payload must contain both "choices" and "answer".')

    choices: dict[str, str] = payload["choices"]
    correct_answer: str = str(payload["answer"])

    if not isinstance(choices, dict):
        raise ValueError('"choices" must be a dictionary mapping letters to option text.')

    resp_normalised = response.strip().lower()

    valid_keys = {str(k).strip().lower() for k in choices.keys()}

    correct_normalised = correct_answer.strip().lower()

    if not (resp_normalised in valid_keys):
        return False

    return resp_normalised == correct_normalised

class _MultipleChoicePlugin(Plugin):
    """Built-in evaluator for classic multiple-choice questions."""

    def load(self):
        """No external resources needed – method present for API symmetry."""
        pass

    def unload(self):
        """Complement to :meth:`load`; nothing to clean up."""
        pass

    def format_prompt(self, options: dict[str, any], question: str) -> str:
        """
        Create a LLM-readable prompt.

        * Validates that ``options["choices"]`` is a non-empty dict.
        * Renders each choice as “A) text”, one per line.
        * Appends the instruction **“Answer with just the letter of the correct choice.”**
        """
        choices_map = options.get("choices")
        if not isinstance(choices_map, dict) or not choices_map:
            raise ValueError(
                "options must contain a non-empty 'choices' dictionary"
            )

        choices_block = "\n".join(
            f"{label.upper()}) {text}" for label, text in choices_map.items()
        )

        prompt = (
            f"{question}\n\n"
            f"{choices_block}\n\n"
            "Answer with just the letter of the correct choice."
        )

        return prompt

    def evaluate(self, options: dict[str, any], response: str) -> dict[str, any]:
        correct = _evaluate_mcq(options, response)
        if correct:
            return {"score": 100, "reason": ""}
        else:
            return {"score" : 0, "reason": "Wrong answer! got: " + response + ", expected: " + options["answer"]}