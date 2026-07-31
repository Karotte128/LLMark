import abc

class Plugin(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None:
        """
        Called when the plugin is loaded.
        This can be used to create any data (e.g. connections to external evaluators).
        """
        pass

    @abc.abstractmethod
    def unload(self) -> None:
        """
        Called when the plugin is unloaded.
        This can be used to destroy any data that has been set up by load()
        """
        pass

    @abc.abstractmethod
    def evaluate(self, data: dict[str, any], response: str) -> dict[str, any]:
        """
        Run the evaluator provided by the plugin.
        Returns the evaluated grade in the following format:
        {"grade": 'float 0-1', reason: 'string'}
        """
        pass