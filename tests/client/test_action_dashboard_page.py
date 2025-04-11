"""Test for the jvcli client dashboard page."""

import os
from pathlib import Path

from pytest_mock import MockerFixture
from streamlit.testing.v1 import AppTest

from jvcli.client.pages.action_dashboard_page import logout


class TestClientActionDashboardPage:
    """Test the JVCLI client dashboard page."""

    def test_render_action_dashboard(self, mocker: MockerFixture) -> None:
        """Test rendering the dashboard page."""
        app_test = AppTest.from_file(
            Path(__file__)
            .resolve()
            .parent.parent.parent.joinpath("jvcli")
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

        # Mock list agents
        mock_agents = mocker.patch("jvcli.client.lib.utils.call_list_agents")
        mock_agents.return_value = [{"id": "test_agent_id", "label": "test_agent_name"}]

        # Mock list actions
        mock_actions = mocker.patch("jvcli.client.lib.utils.call_list_actions")
        mock_actions.return_value = [
            {
                "id": "test_action_id",
                "name": "test_action_name",
                "_package": {
                    "config": {
                        "path": os.path.join(os.path.dirname(__file__), "../fixtures"),
                        "app": True,
                    },
                    "meta": {"title": "Action 1", "type": "interact_action"},
                },
                "label": "Action 1",
                "description": "Test description 1",
                "version": "1.0.0",
                "enabled": True,
            }
        ]

        app_test.run()

        app_test.text_input[0].input("admin@test.com").run()
        app_test.text_input[1].input("password").run()
        app_test.button[0].click().run()

        # assert logged in
        assert app_test.session_state["ROOT_ID"] == "root_id"
        assert app_test.session_state["TOKEN"] == "token"
        assert app_test.session_state["EXPIRATION"] == "expiration"

        # trigger actions dashboard
        app_test.button[2].click().run()

        # assert actions dashboard
        assert app_test.query_params["agent"] == ["test_agent_id"]
        # assert app_test.query_params["request"] == ["GET:/actions"]

    def test_token_removal_from_session_state(self, mocker: MockerFixture) -> None:
        """Test removing the token from session state."""
        # Mock streamlit session state and query params
        mock_session_state = mocker.patch(
            "streamlit.session_state", {"TOKEN": "test_token"}
        )
        mock_query_params = mocker.patch("streamlit.query_params", mocker.MagicMock())
        mock_query_params["token"] = "test_token"

        # Call logout function
        logout()

        # Verify TOKEN was removed from session state
        assert "TOKEN" not in mock_session_state
        assert "token" not in mock_query_params
