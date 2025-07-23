"""Module for registering ALL jvcli CLI commands as jac plugins."""

from __future__ import annotations

from typing import Any

# Import only the needed jvcli command functions
from jvcli.commands.auth import logout as jvcli_logout
from jvcli.commands.create import create as jvcli_create
from jvcli.commands.download import download as jvcli_download
from jvcli.commands.info import info as jvcli_info
from jvcli.commands.publish import publish as jvcli_publish
from jvcli.commands.startproject import startproject as jvcli_startproject

# Import jac components - if not available, skip plugin registration
try:
    from click.testing import CliRunner
    from jaclang.cli.cmdreg import cmd_registry
    from jaclang.runtimelib.machine import hookimpl

    _jac_available = True
except ImportError:
    _jac_available = False

    # Define dummy decorators to avoid syntax errors
    def hookimpl(func: Any) -> Any:  # type: ignore[misc]
        """Dummy hookimpl decorator when jac is not available."""
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
            click_func: Any,
            args: list[str] | None = None,
            input_data: str | None = None,
        ) -> Any:
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

        # Register all commands directly here
        try:
            # ===== STANDALONE COMMANDS =====

            @cmd_registry.register
            def jv_logout() -> None:
                """Log out by clearing the saved token.

                Examples:
                    jac jv-logout
                """
                run_click_command(jvcli_logout)

            @cmd_registry.register
            def jv_startproject(project_name: str, template: str = "basic") -> None:
                """Initialize a new Jivas project with the necessary structure.

                Args:
                    project_name: Name of the project to create
                    template: Template to use (default: basic)

                Examples:
                    jac jv-startproject myproject
                    jac jv-startproject myproject advanced
                """
                args = [project_name]
                if template != "basic":
                    args.extend(["--version", template])
                run_click_command(jvcli_startproject, args)

            # ===== INFO COMMANDS =====

            @cmd_registry.register
            def jv_info_action(name: str, version: str = "") -> None:
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
                run_click_command(jvcli_info, args)

            @cmd_registry.register
            def jv_info_agent(name: str, version: str = "") -> None:
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
                run_click_command(jvcli_info, args)

            # ===== CREATE COMMANDS =====

            @cmd_registry.register
            def jv_create_action(
                name: str, description: str = "", version: str = "0.1.0"
            ) -> None:
                """Create a new action with its folder, associated files, and dependencies.

                Args:
                    name: Name of the action (must be snake_case)
                    description: Description of the action
                    version: Version of the action (default: 0.1.0)

                Examples:
                    jac jv-create-action my_action
                """
                args = ["action", "--name", name]
                if description:
                    args.extend(["--description", description])
                if version != "0.1.0":
                    args.extend(["--version", version])
                run_click_command(jvcli_create, args)

            @cmd_registry.register
            def jv_create_agent(
                name: str, description: str = "", version: str = "0.1.0"
            ) -> None:
                """Create a new agent with its folder and associated files.

                Args:
                    name: Name of the agent (must be snake_case)
                    description: Description of the agent
                    version: Version of the agent (default: 0.1.0)

                Examples:
                    jac jv-create-agent my_agent
                """
                args = ["agent", "--name", name]
                if description:
                    args.extend(["--description", description])
                if version != "0.1.0":
                    args.extend(["--version", version])
                run_click_command(jvcli_create, args)

            # ===== DOWNLOAD COMMANDS =====

            @cmd_registry.register
            def jv_download_action(name: str, version: str = "latest") -> None:
                """Download a JIVAS action package.

                Args:
                    name: Name of the action package to download
                    version: Version to download (default: latest)

                Examples:
                    jac jv-download-action myaction
                    jac jv-download-action myaction 1.0.0
                """
                args = ["action", name]
                if version != "latest":
                    args.extend(["--version", version])
                run_click_command(jvcli_download, args)

            @cmd_registry.register
            def jv_download_agent(name: str, version: str = "latest") -> None:
                """Download a JIVAS agent package.

                Args:
                    name: Name of the agent package to download
                    version: Version to download (default: latest)

                Examples:
                    jac jv-download-agent myagent
                    jac jv-download-agent myagent 1.0.0
                """
                args = ["agent", name]
                if version != "latest":
                    args.extend(["--version", version])
                run_click_command(jvcli_download, args)

            # ===== PUBLISH COMMANDS =====

            @cmd_registry.register
            def jv_publish_action(path: str = ".") -> None:
                """Publish an action to the Jivas repository.

                Args:
                    path: Path to the action directory (default: current directory)

                Examples:
                    jac jv-publish-action
                    jac jv-publish-action ./my-action
                """
                args = ["action"]
                if path != ".":
                    args.extend(["--path", path])
                run_click_command(jvcli_publish, args)

            @cmd_registry.register
            def jv_publish_agent(path: str = ".") -> None:
                """Publish an agent to the Jivas repository.

                Args:
                    path: Path to the agent directory (default: current directory)

                Examples:
                    jac jv-publish-agent
                    jac jv-publish-agent ./my-agent
                """
                args = ["agent"]
                if path != ".":
                    args.extend(["--path", path])
                run_click_command(jvcli_publish, args)

            print("All jvcli commands registered with jac CLI")

        except Exception as e:
            print(f"Error registering jvcli commands: {e}")
            import traceback

            traceback.print_exc()
