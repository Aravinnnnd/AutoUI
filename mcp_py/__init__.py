"""Python port of the MCP package (minimal scaffold).

Expose module-level constants and version information.
"""
from .constants import *  # noqa: F401,F403

__all__ = [
    name for name in globals() if name.isupper() or name == "__version__"
]

__version__ = "0.1.0"
