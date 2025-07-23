"""Tests for jvcli CLI plugin functionality without circular import issues."""

# Get the full path to jac command
import shutil
import subprocess
import sys

import pytest

JAC_CMD = shutil.which("jac") or "/home/thami/personal/my/bin/jac"


class TestJvcliCliPlugin:
    """Test jvcli CLI plugin integration without importing plugin directly."""

    def test_jac_commands_available_in_help(self) -> None:
        """Test that jvcli commands are available in jac --help output."""
        # Act
        result = subprocess.run(
            [JAC_CMD, "--help"], capture_output=True, text=True, timeout=30
        )

        # Assert
        assert result.returncode == 0
        assert "jv_logout" in result.stdout
        assert "jv_startproject" in result.stdout
        assert "jv_info_action" in result.stdout
        assert "jv_info_agent" in result.stdout
        assert "jv_create_action" in result.stdout
        assert "jv_create_agent" in result.stdout
        assert "jv_download_action" in result.stdout
        assert "jv_download_agent" in result.stdout
        assert "jv_publish_action" in result.stdout
        assert "jv_publish_agent" in result.stdout

    def test_jac_logout_command_execution(self) -> None:
        """Test that jac jv_logout command executes successfully."""
        # Act
        result = subprocess.run(
            [JAC_CMD, "jv_logout"], capture_output=True, text=True, timeout=30
        )

        # Assert
        assert result.returncode == 0
        assert "You have been logged out" in result.stdout
        assert "All jvcli commands registered with jac CLI" in result.stdout

    @pytest.mark.parametrize(
        "command,expected_text",
        [
            ("jv_logout", "Log out by clearing the saved token"),
            ("jv_startproject", "Initialize a new Jivas project"),
            ("jv_info_action", "Get info for an action package"),
            ("jv_info_agent", "Get info for an agent package"),
            ("jv_create_action", "Create a new action"),
            ("jv_create_agent", "Create a new agent"),
            ("jv_download_action", "Download a JIVAS action package"),
            ("jv_download_agent", "Download a JIVAS agent package"),
            ("jv_publish_action", "Publish an action to the Jivas repository"),
            ("jv_publish_agent", "Publish an agent to the Jivas repository"),
        ],
    )
    def test_command_descriptions(self, command: str, expected_text: str) -> None:
        """Test that command descriptions are properly displayed."""
        result = subprocess.run(
            [JAC_CMD, command, "--help"], capture_output=True, text=True, timeout=30
        )

        assert result.returncode == 0
        assert expected_text in result.stdout

    def test_entry_point_registration(self) -> None:
        """Test that jvcli is properly registered as a jac entry point."""
        try:
            from importlib.metadata import entry_points

            # Use modern importlib.metadata
            eps = entry_points(group="jac")
            jvcli_entries = [ep for ep in eps if ep.name == "jvcli"]
            assert len(jvcli_entries) == 1
            assert jvcli_entries[0].value == "jvcli.plugin.cli:JacCmd"
        except ImportError:
            # Fallback to pkg_resources for older Python
            import pkg_resources

            jvcli_entries_iter = pkg_resources.iter_entry_points("jac", "jvcli")
            jvcli_entries = list(jvcli_entries_iter)  # type: ignore[arg-type]
            assert len(jvcli_entries) == 1
            # For pkg_resources, entry points have different attributes
            entry_point = jvcli_entries[0]
            # Use the string representation which is standardized
            assert str(entry_point).endswith("jvcli.plugin.cli:JacCmd")

    def test_package_imports_successfully(self) -> None:
        """Test that the package can be imported without issues."""
        import jvcli

        # Check that the package has version info
        assert hasattr(jvcli, "__version__")
        assert jvcli.__version__ == "2.0.31"

    def test_no_circular_imports_during_runtime(self) -> None:
        """Test that there are no circular import issues during plugin loading."""
        # This test runs the actual jac command to ensure plugin loads correctly
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import jaclang; print('Plugin loading successful')",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "Plugin loading successful" in result.stdout

    def test_all_commands_have_help(self) -> None:
        """Test that all jvcli commands provide help output."""
        commands = [
            "jv_logout",
            "jv_startproject",
            "jv_info_action",
            "jv_info_agent",
            "jv_create_action",
            "jv_create_agent",
            "jv_download_action",
            "jv_download_agent",
            "jv_publish_action",
            "jv_publish_agent",
        ]

        for cmd in commands:
            result = subprocess.run(
                [JAC_CMD, cmd, "--help"], capture_output=True, text=True, timeout=30
            )

            # Assert
            assert result.returncode == 0, f"Command {cmd} --help failed"
            assert (
                "usage:" in result.stdout.lower()
            ), f"Command {cmd} help missing usage"
            assert "All jvcli commands registered with jac CLI" in result.stdout

    def test_jac_startproject_help_shows_parameters(self) -> None:
        """Test that jv_startproject command shows correct parameters."""
        result = subprocess.run(
            [JAC_CMD, "jv_startproject", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "project_name" in result.stdout
        assert "-t TEMPLATE" in result.stdout or "--template" in result.stdout

    def test_jac_info_commands_show_parameters(self) -> None:
        """Test that info commands show correct parameters."""
        for cmd in ["jv_info_action", "jv_info_agent"]:
            result = subprocess.run(
                [JAC_CMD, cmd, "--help"], capture_output=True, text=True, timeout=30
            )

            assert result.returncode == 0
            assert "name" in result.stdout
            assert "-v VERSION" in result.stdout or "--version" in result.stdout

    def test_jac_create_commands_show_parameters(self) -> None:
        """Test that create commands show correct parameters."""
        for cmd in ["jv_create_action", "jv_create_agent"]:
            result = subprocess.run(
                [JAC_CMD, cmd, "--help"], capture_output=True, text=True, timeout=30
            )

            assert result.returncode == 0
            assert "name" in result.stdout
            assert "-d DESCRIPTION" in result.stdout or "--description" in result.stdout
            assert "-v VERSION" in result.stdout or "--version" in result.stdout

    def test_jac_download_commands_show_parameters(self) -> None:
        """Test that download commands show correct parameters."""
        for cmd in ["jv_download_action", "jv_download_agent"]:
            result = subprocess.run(
                [JAC_CMD, cmd, "--help"], capture_output=True, text=True, timeout=30
            )

            assert result.returncode == 0
            assert "name" in result.stdout
            assert "-v VERSION" in result.stdout or "--version" in result.stdout

    def test_jac_publish_commands_show_parameters(self) -> None:
        """Test that publish commands show correct parameters."""
        for cmd in ["jv_publish_action", "jv_publish_agent"]:
            result = subprocess.run(
                [JAC_CMD, cmd, "--help"], capture_output=True, text=True, timeout=30
            )

            assert result.returncode == 0
            assert "path" in result.stdout
