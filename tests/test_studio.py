"""Tests for the studio command."""

from bson import ObjectId
from click.testing import CliRunner
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from jvcli.commands.studio import get_graph, get_users, launch


class TestStudio:
    """Test cases for the studio command."""

    # Launch studio successfully on default port 8989
    def test_launch_studio_default_port(self, mocker: MockerFixture) -> None:
        """Test launching studio with default port."""
        # Mock FastAPI and its dependencies
        mock_fastapi = mocker.patch("fastapi.FastAPI")
        mock_app = mocker.MagicMock()
        mock_fastapi.return_value = mock_app

        # Mock uvicorn run
        mock_run = mocker.patch("jvcli.commands.studio.run")

        # Mock Path operations
        mock_path = mocker.patch("pathlib.Path")
        mock_path_instance = mocker.MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.resolve.return_value.parent.parent.joinpath.return_value = (
            "mock/studio/path"
        )

        # Mock click.echo
        mock_echo = mocker.patch("click.echo")

        # Create CLI runner
        runner = CliRunner()

        # Run the command
        result = runner.invoke(launch)

        # Verify the command executed successfully
        assert result.exit_code == 0

        # Verify proper port was used
        mock_run.assert_called_once_with(mock_app, host="0.0.0.0", port=8989)

        # Verify studio launch message was displayed
        mock_echo.assert_called_once_with("Launching Jivas Studio on port 8989...")

    def test_get_graph_endpoint(self, mocker: MockerFixture) -> None:
        """Test the /graph endpoint."""

        # Mock database collections
        mock_get_collection = mocker.patch(
            "jvcli.commands.studio.NodeAnchor.Collection.get_collection"
        )
        mock_node_collection = mocker.MagicMock()
        mock_edge_collection = mocker.MagicMock()
        mock_get_collection.side_effect = lambda name: (
            mock_node_collection if name == "node" else mock_edge_collection
        )

        # Mock database responses
        mock_node_collection.find.return_value = [
            {
                "_id": ObjectId("507f191e810c19729de860ea"),
                "root": ObjectId("507f191e810c19729de860eb"),
                "architype": "TestNode",
                "name": "Node1",
            }
        ]
        mock_edge_collection.find.return_value = [
            {
                "_id": ObjectId("507f191e810c19729de860ec"),
                "root": ObjectId("507f191e810c19729de860eb"),
                "name": "Edge1",
                "source": "Node1",
                "target": "Node2",
                "architype": "TestEdge",
            }
        ]

        # Create FastAPI app and test client
        app = FastAPI()
        app.add_api_route("/graph", endpoint=get_graph, methods=["GET"])
        client = TestClient(app)

        # Send GET request
        response = client.get("/graph", params={"root": "507f191e810c19729de860eb"})

        # Verify response
        assert response.status_code == 200
        expected_response = {
            "nodes": [
                {
                    "id": "507f191e810c19729de860ea",  # pragma: allowlist secret
                    "data": "TestNode",
                    "name": "Node1",
                }
            ],
            "edges": [
                {
                    "id": "507f191e810c19729de860ec",  # pragma: allowlist secret
                    "name": "Edge1",
                    "source": "Node1",
                    "target": "Node2",
                    "data": "TestEdge",
                }
            ],
        }
        assert response.json() == expected_response

    def test_get_users_endpoint(self, mocker: MockerFixture) -> None:
        """Test the /users endpoint."""

        # Mock database collections
        mock_get_collection = mocker.patch(
            "jvcli.commands.studio.NodeAnchor.Collection.get_collection"
        )
        mock_user_collection = mocker.MagicMock()
        mock_get_collection.side_effect = lambda name: (
            mock_user_collection if name == "user" else None
        )

        # Mock database response
        mock_user_collection.find.return_value = [
            {
                "_id": ObjectId("507f191e810c19729de860ed"),
                "root_id": "507f191e810c19729de860eb",
                "email": "user@example.com",
            }
        ]

        # Create FastAPI app and test client
        app = FastAPI()
        app.add_api_route("/users", endpoint=get_users, methods=["GET"])
        client = TestClient(app)

        # Send GET request
        response = client.get("/users")

        # Verify response
        assert response.status_code == 200
        expected_response = [
            {
                "id": "507f191e810c19729de860ed",  # pragma: allowlist secret
                "root_id": "507f191e810c19729de860eb",
                "email": "user@example.com",
            }
        ]
        assert response.json() == expected_response
