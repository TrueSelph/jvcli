"""Tests for the create module."""

from click.testing import CliRunner
from pytest_mock import MockerFixture

from jvcli import __supported__jivas__versions__
from jvcli.commands.create import create_action
from jvcli.utils import TEMPLATES_DIR


class TestCreateCommand:
    """Test cases for the create command."""

    def test_create_action_with_valid_name_and_defaults(
        self, mocker: MockerFixture
    ) -> None:
        """Test creating an action with valid name and default values."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mock_makedirs = mocker.patch("os.makedirs")
        mock_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_click = mocker.patch("click.secho")

        runner = CliRunner()
        result = runner.invoke(create_action, ["--name", "test_action"])

        assert result.exit_code == 0
        mock_makedirs.assert_has_calls(
            [
                mocker.call("./actions/testuser/test_action", exist_ok=True),
                mocker.call("./actions/testuser/test_action/app", exist_ok=True),
            ],
            any_order=True,
        )

        mock_open.assert_any_call("./actions/testuser/test_action/info.yaml", "w")
        mock_open.assert_any_call("./actions/testuser/test_action/app/app.py", "w")

        mock_click.assert_called_with(
            "Action 'test_action' created successfully in ./actions/testuser/test_action!",
            fg="green",
            bold=True,
        )

    def test_create_action_generates_correct_file_structure(
        self, mocker: MockerFixture
    ) -> None:
        """Test that create_action generates the correct file structure."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mock_makedirs = mocker.patch("os.makedirs")
        mock_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_click = mocker.patch("click.secho")

        runner = CliRunner()
        result = runner.invoke(create_action, ["--name", "test_action"])

        assert result.exit_code == 0
        mock_makedirs.assert_has_calls(
            [
                mocker.call("./actions/testuser/test_action", exist_ok=True),
                mocker.call("./actions/testuser/test_action/app", exist_ok=True),
            ],
            any_order=True,
        )

        mock_open.assert_any_call("./actions/testuser/test_action/info.yaml", "w")
        mock_open.assert_any_call("./actions/testuser/test_action/lib.jac", "w")
        mock_open.assert_any_call("./actions/testuser/test_action/test_action.jac", "w")
        mock_open.assert_any_call("./actions/testuser/test_action/app/app.py", "w")

        mock_click.assert_called_with(
            "Action 'test_action' created successfully in ./actions/testuser/test_action!",
            fg="green",
            bold=True,
        )

    def test_appends_correct_suffix_based_on_action_type(
        self, mocker: MockerFixture
    ) -> None:
        """Test that the correct suffix is appended based on action type."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mock_makedirs = mocker.patch("os.makedirs")
        mocker.patch("builtins.open", mocker.mock_open())
        mock_click = mocker.patch("click.secho")

        runner = CliRunner()
        result = runner.invoke(
            create_action, ["--name", "test", "--type", "interact_action"]
        )

        assert result.exit_code == 0
        expected_name = "test_interact_action"
        mock_makedirs.assert_any_call(
            f"./actions/testuser/{expected_name}", exist_ok=True
        )
        mock_click.assert_called_with(
            f"Action '{expected_name}' created successfully in ./actions/testuser/{expected_name}!",
            fg="green",
            bold=True,
        )

    def test_create_action_creates_documentation_files(
        self, mocker: MockerFixture
    ) -> None:
        """Test that documentation files are created with substituted values."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mocker.patch("os.makedirs")
        mocker.patch("builtins.open", mocker.mock_open())
        mocker.patch("click.secho")
        mock_create_docs = mocker.patch("jvcli.commands.create.create_docs")

        runner = CliRunner()
        result = runner.invoke(create_action, ["--name", "test_action"])

        assert result.exit_code == 0
        mock_create_docs.assert_called_once_with(
            "./actions/testuser/test_action",
            "Test Action",
            "0.0.1",
            "action",
            "No description provided.",
        )

    def test_create_action_with_invalid_jivas_version(
        self, mocker: MockerFixture
    ) -> None:
        """Test handling of invalid Jivas version."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mock_click = mocker.patch("click.secho")
        runner = CliRunner()
        result = runner.invoke(
            create_action, ["--name", "test_action", "--jivas_version", "1.0.0"]
        )
        assert result.exit_code == 0
        mock_click.assert_called_with(
            "Jivas version 1.0.0 is not supported. Supported versions are: {}.".format(
                str(__supported__jivas__versions__)
            ),
            fg="red",
        )

    def test_create_action_appends_suffix_when_missing(
        self, mocker: MockerFixture
    ) -> None:
        """Test that the suffix is appended to the name if it does not already have it."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mock_makedirs = mocker.patch("os.makedirs")
        mock_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_click = mocker.patch("click.secho")

        runner = CliRunner()
        result = runner.invoke(
            create_action, ["--name", "testaction"]  # Name without suffix
        )

        assert result.exit_code == 0
        expected_name_with_suffix = "testaction_action"
        mock_makedirs.assert_has_calls(
            [
                mocker.call(
                    f"./actions/testuser/{expected_name_with_suffix}", exist_ok=True
                ),
                mocker.call(
                    f"./actions/testuser/{expected_name_with_suffix}/app", exist_ok=True
                ),
            ],
            any_order=True,
        )

        mock_open.assert_any_call(
            f"./actions/testuser/{expected_name_with_suffix}/info.yaml", "w"
        )
        mock_open.assert_any_call(
            f"./actions/testuser/{expected_name_with_suffix}/app/app.py", "w"
        )

        mock_click.assert_called_with(
            f"Action '{expected_name_with_suffix}' created successfully in ./actions/testuser/{expected_name_with_suffix}!",
            fg="green",
            bold=True,
        )

    def test_create_action_template_not_found(self, mocker: MockerFixture) -> None:
        """Test behavior when the template file is not found for the specified version."""
        mock_load_token = mocker.patch("jvcli.commands.create.load_token")
        mock_load_token.return_value = {
            "email": "test@example.com",
            "namespaces": {"default": "testuser"},
        }
        mocker.patch("os.makedirs")
        mocker.patch("builtins.open", mocker.mock_open())
        mock_click = mocker.patch("click.secho")
        mocker.patch("os.path.exists", return_value=False)

        runner = CliRunner()
        result = runner.invoke(
            create_action, ["--name", "test_action", "--jivas_version", "2.0.0"]
        )

        assert result.exit_code == 0
        mock_click.assert_called_with(
            f"Template for version 2.0.0 not found in {TEMPLATES_DIR}.", fg="red"
        )
