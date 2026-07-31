from .plugin_manager import _PluginManager
from .plugin import Plugin
from .internal.multiple_choice_evaluator import MultipleChoicePlugin

from pathlib import Path
import importlib.util

class Evaluator:
    def __init__(self, ext_plugins: dict[str, Plugin]) -> None:
        self._pm = _PluginManager()
        self._ext_plugins = ext_plugins
        self._int_plugins: dict[str, Plugin] = {
            "multiple-choice": MultipleChoicePlugin()
        }

    def _load_from_file(self, pathstr: str) -> Plugin:

        path = Path(pathstr)

        if not path.exists():
            raise FileNotFoundError(path)

        module_name = f"file_{path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from '{path}'")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "Plugin"):
            raise TypeError(
                f"'{path}' does not define a Plugin class"
            )

        plugin = module.FilePlugin()

        if not isinstance(plugin, Plugin):
            raise TypeError(
                f"Plugin in '{path}' does not inherit from Plugin"
            )

        return plugin

    def _loadEvaluator(self, source: str, alias: str) -> None:
        try:
            ptype, pname = source.split(":", 1)
        except ValueError as exc:
            raise ValueError(
                f"Invalid plugin source description '{source}'. Expected format 'type:name'."
            ) from exc

        ptype = ptype.strip().lower()
        pname = pname.strip()

        if ptype == "ext":
            try:
                plugin = self._ext_plugins[pname]
            except KeyError as exc:
                raise KeyError(f"No external plugin named '{pname}'.") from exc

        elif ptype == "int":
            try:
                plugin = self._int_plugins[pname]
            except KeyError as exc:
                raise KeyError(f"No internal plugin class called '{pname}'.") from exc

        elif ptype == "file":
            plugin = self._load_from_file(pname)

        else:
            raise ValueError(
                f"Unsupported plugin type '{ptype}'. "
                "Supported source types are 'ext', 'int' and 'file'."
            )

        self._pm._register(alias, plugin)

    def loadEvaluators(self, eval_sources: dict[str, str]) -> None:
        self._pm._unload_all()
        for source, alias in eval_sources.items():
            self._loadEvaluator(source, alias)
        self._pm._load_all()

    def unloadEvaluators(self) -> None:
        self._pm._unload_all()

    def format_prompt(self, formatter: str, options: dict[str, any], question: str) -> str:
        return self._pm._format_prompt(formatter, options, question)

    def evaluate(self, evaluator: str, options: dict[str, any], response: str) -> dict[str, any]:
        try:
            return self._pm._evaluate(evaluator, options, response)
        except Exception as exc:
            return {
                "score": 0,
                "reason": "Evalutating resulted in exception: " + str(exc)
            }