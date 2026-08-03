from ..plugin import Plugin

from .mcq_plugin import _MultipleChoicePlugin
from .string_plugin import _StringMatchPlugin
from .number_plugin import _NumberPlugin

internal_plugins: dict[str, Plugin] = {
    "multiple-choice": _MultipleChoicePlugin(),
    "string": _StringMatchPlugin(),
    "number": _NumberPlugin()
}