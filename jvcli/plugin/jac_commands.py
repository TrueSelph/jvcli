"""Module for registering ALL jvcli CLI commands as jac plugins."""

from __future__ import annotations

from typing import Callable

from jvcli.commands.info import info as jv_info

try:
    from click.testing import CliRunner
    from jaclang.cli.cmdreg import cmd_registry
    from jaclang.runtimelib.machine import hookimpl

    _jac_available = True
except ImportError:
    _jac_available = False

    def hookimpl(func: Callable) -> Callable:
        """Dummy hookimpl decorator if jaclang is not available."""
        return func

    cmd_registry = None  # type: ignore


class JacCmd:
    """Jvcli Jac Plugin - ALL CLI commands for Jivas Package Repository."""

    @staticmethod
    @hookimpl
    def create_cmd() -> None:
        """Create ALL jvcli CLI commands for jac."""
        if not _jac_available:
            print("Warning: jaclang not available, jvcli commands not registered")
            return

        # Helper function to run Click commands
        def run_click_command(
            click_func: Callable,
            args: list[str] | None = None,
            input_data: str | None = None,
        ) -> None:
            """Helper to run Click commands via CliRunner."""
            try:
                runner = CliRunner()
                result = runner.invoke(click_func, args or [], input=input_data)

                if result.output:
                    print(result.output.strip())
                if result.exit_code != 0:
                    print(f"Error: Command failed with exit code {result.exit_code}")

            except Exception as e:
                print(f"Error executing command: {e}")

            @cmd_registry.register
            def info_action(name: str, version: str = "") -> None:
                """Get info for an action package by name and version.

                Args:
                    name: Name of the action package
                    version: Version of the package (optional)

                Examples:
                    jac jv-info-action myaction
                    jac jv-info-action myaction 1.0.0
                """
                args = ["action", name]
                if version:
                    args.append(version)
                run_click_command(jv_info, args)

            @cmd_registry.register
            def info_agent(name: str, version: str = "") -> None:
                """Get info for an agent package by name and version.

                Args:
                    name: Name of the agent package
                    version: Version of the package (optional)

                Examples:
                    jac jv-info-agent myagent
                    jac jv-info-agent myagent 1.0.0
                """
                args = ["agent", name]
                if version:
                    args.append(version)
                run_click_command(jv_info, args)
