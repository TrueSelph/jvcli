"""Tests for the jvclient module."""

from pathlib import Path

from click.testing import CliRunner
from pytest_mock import MockerFixture
from streamlit.testing.v1 import AppTest

from jvcli.commands.client import launch


class TestClient:
    """Test cases for the client command."""

    def test_launch_client_default_port(self, mocker: MockerFixture) -> None:
        """Test launching client with default port."""
        # Mock subprocess.call
        mock_call = mocker.patch("subprocess.call")

        # Create CLI runner
        runner = CliRunner()

        # Run the command
        result = runner.invoke(launch)

        # Verify the command executed successfully
        assert result.exit_code == 0

        # Verify proper port was used
        mock_call.assert_called_once_with(
            [
                "streamlit",
                "run",
                "--server.port=8501",
                "--client.showSidebarNavigation=False",
                "--client.showErrorDetails=False",
                "--global.showWarningOnDirectExecution=False",
                f"{Path(__file__).resolve().parent.parent.joinpath('jvcli').joinpath('client').joinpath('app.py').resolve().__str__()}",
            ]
        )

    def test_client_init_login_form(self, mocker: MockerFixture) -> None:
        """Test init render of client app with login form."""

        app_test = AppTest.from_file(
            Path(__file__)
            .resolve()
            .parent.parent.joinpath("jvcli")
            .joinpath("client")
            .joinpath("app.py")
            .resolve()
            .__str__()
        )

        app_test.run()

        assert app_test.header[0].body == "Login"

    def test_client_login(self, mocker: MockerFixture) -> None:
        """Test login form submission."""

        app_test = AppTest.from_file(
            Path(__file__)
            .resolve()
            .parent.parent.joinpath("jvcli")
            .joinpath("client")
            .joinpath("app.py")
            .resolve()
            .__str__()
        )

        # Mock post request
        mocker_login = mocker.patch("jvcli.client.app.requests.post")
        mocker_login.return_value.status_code = 200
        mocker_login.return_value.json.return_value = {
            "user": {"root_id": "root_id", "expiration": "expiration"},
            "token": "token",
        }
        mock_agents = mocker.patch("jvcli.client.app.call_list_agents")
        mock_agents.return_value = [{"id": "test_agent_id", "name": "test_agent_name"}]

        mock_actions = mocker.patch("jvcli.client.app.call_list_actions")
        mock_actions.return_value = [
            {"id": "test_action_id", "name": "test_action_name"}
        ]
        app_test.run()

        app_test.text_input[0].input("admin@test.com").run()
        app_test.text_input[1].input("password").run()
        app_test.button[0].click().run()

        assert app_test.session_state["ROOT_ID"] == "root_id"
        assert app_test.session_state["TOKEN"] == "token"
        assert app_test.session_state["EXPIRATION"] == "expiration"
