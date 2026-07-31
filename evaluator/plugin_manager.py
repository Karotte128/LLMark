from .plugin import Plugin

class _PluginManager:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def _register(self, name: str, plugin: Plugin) -> None:
            if not isinstance(plugin, Plugin):
                raise TypeError(
                    f"{name} does not inherit from Plugin"
                )

            if name in self._plugins:
                raise ValueError(f"Plugin '{name}' is already registered.")

            self._plugins[name] = plugin

    def _load_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.load()

    def _unload_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.unload()

    def _format_prompt(self, formatter: str, options: dict[str, any], question: str) -> str:
        try:
            return self._plugins[formatter].format_prompt(options, question)
        except KeyError as exc:
            raise ValueError(f"Plugin '{formatter}' is not available.") from exc

    def _evaluate(self, evaluator: str, options: dict[str, any], response: str) -> dict[str, any]:
        try:
            return self._plugins[evaluator].evaluate(options, response)
        except KeyError as exc:
            raise ValueError(f"Plugin '{evaluator}' is not available.") from exc