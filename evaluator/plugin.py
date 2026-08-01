import abc

class Plugin(abc.ABC):
    """
    Abstract base class that every evaluator plugin must implement.

    Required lifecycle methods:
        * :meth:`load`   – allocate resources (e.g. DB connections).
        * :meth:`unload` – clean up those resources.
        * :meth:`format_prompt` – turn a question + options into the exact prompt string that will be sent to the LLM.
        * :meth:`evaluate` – score the raw model response and return a dict: {"score": int, "reason": str}
    """

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
    def format_prompt(self, options: dict[str, any], question: str) -> str:
        """
        Formats the prompt so the evaluator can parse the response.
        """
        pass

    @abc.abstractmethod
    def evaluate(self, options: dict[str, any], response: str) -> dict[str, any]:
        """
        Run the evaluator provided by the plugin.
        Returns the evaluated score in the following format:
        {"score": 'int 0-100', reason: 'string'}
        """
        pass