"""
jvcli package initialization.

This package provides the CLI plugin for Jivas Package Repository integration with jac.
"""

__version__ = "2.0.31"
__supported__jivas__versions__ = ["2.1.0"]


def load_plugin() -> str:
    """Load the jvcli plugin by registering commands with jac."""
    try:
        # Import command modules to register them with jac's cmd_registry
        from jvcli.plugin.cli import JacCmd  # noqa: F401

        return "jvcli plugin loaded successfully"
    except ImportError as e:
        return f"jvcli plugin could not be loaded: {e}"


# Don't auto-import the plugin class to avoid circular imports
# The plugin will be loaded by jac when needed via the entry point
__all__ = ["load_plugin"]
