from ..plugin import Plugin

from .mcq_plugin import _MultipleChoicePlugin

internal_plugins: dict[str, Plugin] = {
    "multiple-choice": _MultipleChoicePlugin()
}