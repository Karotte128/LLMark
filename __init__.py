"""
Top-level package for **LLMark**.

Exports:
* :class:`Plugin` – abstract base class for all evaluators.
* :class:`LLMark` – core orchestrator that runs a benchmark test set.

The ``__all__`` list is corrected to expose both names.
"""

from .evaluator.plugin import Plugin
from .llmark import LLMark

__all__ = ["Plugin", "LLMark"]