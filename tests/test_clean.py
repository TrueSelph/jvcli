"""Tests for the clean command."""

import subprocess

from click.testing import CliRunner
from pytest_mock import MockerFixture

from jvcli.commands.clean import clean


class TestCleanCommand:
    """Test cases for the clean command."""

    def test_clean_success(self, mocker: MockerFixture) -> None:
        """Test successful cleaning with jac clean command."""
        # Mock subprocess.run
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)

        runner = CliRunner()
        result = runner.invoke(clean)

        assert result.exit_code == 0
        mock_run.assert_called_once_with(["jac", "clean"], check=True)
        assert "Successfully cleaned directory." in result.output

    def test_clean_subprocess_error(self, mocker: MockerFixture) -> None:
        """Test handling of subprocess error."""
        # Mock subprocess.run to raise CalledProcessError
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(1, ["jac", "clean"])

        runner = CliRunner()
        result = runner.invoke(clean)

        assert result.exit_code == 1
        assert "Error running jac clean" in result.output

    def test_clean_unexpected_error(self, mocker: MockerFixture) -> None:
        """Test handling of unexpected errors."""
        # Mock subprocess.run to raise an unexpected exception
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = Exception("Unexpected test error")

        runner = CliRunner()
        result = runner.invoke(clean)

        assert result.exit_code == 1
        assert "Unexpected error" in result.output

    def test_clean_nonzero_returncode(self, mocker: MockerFixture) -> None:
        """Test handling of non-zero return code without exception."""
        # Mock subprocess.run to return non-zero code without raising exception
        # Note: This test is for completeness, but with check=True in the implementation,
        # a non-zero return code would actually raise CalledProcessError
        mock_run = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(clean)

        assert result.exit_code == 1
        assert "Failed to clean directory." in result.output
