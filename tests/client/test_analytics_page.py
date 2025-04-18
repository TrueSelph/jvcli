"""Test for the JVCLI client analytics page."""

import datetime

from pytest_mock import MockerFixture

from jvcli.client.lib.utils import JIVAS_BASE_URL
from jvcli.client.pages.analytics_page import (
    channels_chart,
    interactions_chart,
    render,
    users_chart,
)


class TestClientAnalyticsPage:
    """Test the JVCLI client analytics page."""

    def test_render_analytics_with_valid_inputs(self, mocker: MockerFixture) -> None:
        """Test rendering analytics with valid inputs."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.pages.analytics_page.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock session state
        mocker.patch(
            "streamlit.session_state", {"selected_agent": {"id": "test_agent_id"}}
        )

        # Mock streamlit widgets
        mocker.patch("streamlit.header")
        mock_date_input = mocker.patch("streamlit.date_input")
        mock_date_input.return_value = (
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31),
        )
        mocker.patch(
            "jvcli.client.pages.analytics_page.st.columns", return_value=(1, 2, 3)
        )
        mocker.patch(
            "jvcli.client.pages.analytics_page.st_javascript",
            return_value="test_timezone",
        )

        # Mock chart functions
        mock_interactions = mocker.patch(
            "jvcli.client.pages.analytics_page.interactions_chart"
        )
        mock_users = mocker.patch("jvcli.client.pages.analytics_page.users_chart")
        mock_channels = mocker.patch("jvcli.client.pages.analytics_page.channels_chart")

        # Mock router
        mock_router = mocker.Mock()

        # Call function
        render(mock_router)

        # Verify chart functions were called with correct params
        mock_interactions.assert_called_once()
        mock_users.assert_called_once()
        mock_channels.assert_called_once()

    def test_interactions_chart_successful_api_call(
        self, mocker: MockerFixture
    ) -> None:
        """Test interactions chart with a successful API call."""
        # Mock dependencies
        mock_container = mocker.patch("streamlit.container")
        mock_subheader = mocker.patch("streamlit.subheader")
        mock_line_chart = mocker.patch("streamlit.line_chart")
        mock_metric = mocker.Mock()
        mock_requests = mocker.patch("requests.post")

        # Setup test data
        test_date = datetime.date(2024, 1, 1)
        test_response_data = {
            "reports": [{"data": [{"date": "2024-01-01", "count": 10}], "total": 100}]
        }
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = test_response_data

        # Call function
        interactions_chart(
            start_date=test_date,
            end_date=test_date,
            agent_id="test_agent",
            token="test_token",
            metric_col=mock_metric,
            timezone="UTC",
        )

        # Verify API call
        mock_requests.assert_called_once_with(
            url=f"{JIVAS_BASE_URL}/walker/get_interactions_by_date",
            json={
                "agent_id": "test_agent",
                "reporting": True,
                "start_date": test_date.isoformat(),
                "end_date": test_date.isoformat(),
                "timezone": "UTC",
            },
            headers={"Authorization": "Bearer test_token"},
        )

        # Verify chart rendering
        mock_container.assert_called_once()
        mock_subheader.assert_called_once_with("Interactions by Date")
        mock_line_chart.assert_called_once()
        mock_metric.metric.assert_called_once_with("Interactions", 100)

    def test_users_chart_successful_api_call(self, mocker: MockerFixture) -> None:
        """Test users chart with a successful API call."""
        # Mock streamlit widgets
        mock_container = mocker.patch("streamlit.container")
        mock_subheader = mocker.patch("streamlit.subheader")
        mock_line_chart = mocker.patch("streamlit.line_chart")
        mock_metric = mocker.Mock()
        mock_metric_col = mocker.Mock()
        mock_metric_col.metric = mock_metric

        # Mock requests.post response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "reports": [
                {
                    "data": [
                        {"date": "2024-01-01", "count": 10},
                        {"date": "2024-01-02", "count": 20},
                    ],
                    "total": 30,
                }
            ]
        }
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Test inputs
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 31)
        agent_id = "test_agent_id"
        token = "test_token"
        timezone = "UTC"

        # Call function
        users_chart(start_date, end_date, agent_id, token, mock_metric_col, timezone)

        # Verify API call
        mock_post.assert_called_once_with(
            url=f"{JIVAS_BASE_URL}/walker/get_users_by_date",
            json={
                "agent_id": agent_id,
                "reporting": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": timezone,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Verify streamlit widgets were called
        mock_container.assert_called_once()
        mock_subheader.assert_called_once_with("Users by Date")
        mock_line_chart.assert_called_once()
        mock_metric.assert_called_once_with("Users", 30)

    def test_channels_chart_successful_api_call(self, mocker: MockerFixture) -> None:
        """Test channels chart with a successful API call."""
        # Mock streamlit components
        mock_container = mocker.patch("streamlit.container")
        mock_subheader = mocker.patch("streamlit.subheader")
        mock_line_chart = mocker.patch("streamlit.line_chart")
        mock_metric = mocker.Mock()

        # Mock requests post call
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "reports": [
                {
                    "data": [
                        {"date": "2024-01-01", "count": 5},
                        {"date": "2024-01-02", "count": 10},
                    ],
                    "total": 15,
                }
            ]
        }
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Test inputs
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 2)
        agent_id = "test_agent"
        token = "test_token"
        timezone = "UTC"

        # Call function
        channels_chart(start_date, end_date, agent_id, token, mock_metric, timezone)

        # Verify API call
        mock_post.assert_called_once_with(
            url=f"{JIVAS_BASE_URL}/walker/get_channels_by_date",
            json={
                "agent_id": agent_id,
                "reporting": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": timezone,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Verify streamlit components called
        mock_container.assert_called_once()
        mock_subheader.assert_called_once_with("Channels by Date")
        mock_line_chart.assert_called_once()
        mock_metric.metric.assert_called_once_with("Channels", 15)
