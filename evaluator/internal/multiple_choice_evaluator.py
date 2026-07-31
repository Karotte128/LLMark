from ..plugin import Plugin

def _evaluate_mcq(payload: dict[str, str], response: str) -> bool:
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

class MultipleChoicePlugin(Plugin):
    """multiple choiche plugin"""

    def load(self):
        pass

    def unload(self):
        pass

    def format_prompt(self, question: str, options: dict[str, any]) -> str:
        pass

    def evaluate(self, options: dict[str, any], response: str) -> dict[str, any]:
        correct = _evaluate_mcq(options, response)
        if correct:
            return {"score": 100, "reason": ""}
        else:
            return {"score" : 0, "reason": "Wrong answer! got: " + response + ", expected: " + options["answer"]}