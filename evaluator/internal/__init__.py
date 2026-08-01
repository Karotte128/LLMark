from ..plugin import Plugin

from .mcq_plugin import _MultipleChoicePlugin
from .string_plugin import _StringMatchPlugin

internal_plugins: dict[str, Plugin] = {
    "multiple-choice": _MultipleChoicePlugin(),
    "string": _StringMatchPlugin()
}