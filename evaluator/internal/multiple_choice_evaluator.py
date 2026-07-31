from ..plugin import Plugin

class MultipleChoicePlugin(Plugin):
    """multiple choiche plugin"""

    def load(self):
        pass

    def unload(self):
        pass

    def evaluate(self, data: dict[str, any], response: str) -> dict[str, any]:
        print("running internal/multiple-choice")
        #TODO: implement the actual logic
        pass