"""Tests for the jvcli.auth module."""

import json

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from jvcli.auth import (
    TOKEN_FILE,
    clean_namespaces,
    delete_token,
    load_namespaces,
    load_token,
    save_token,
)
from jvcli.commands.auth import login, logout, signup


class TestAuth:
    """Test cases for the authentication module."""

    def test_save_token_with_valid_data(self, mocker: MockerFixture) -> None:
        """Save token with valid data and verify file content matches expected format."""
        mock_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_json = mocker.patch("json.dump")

        token = "test_token"
        namespaces = {"default": "@test", "groups": ["@group1"]}
        email = "test@example.com"

        save_token(token, namespaces, email)

        expected_data = {
            "token": token,
            "namespaces": {"default": "test", "groups": ["group1"]},
            "email": email,
        }
        mock_json.assert_called_once_with(expected_data, mock_open())

    def test_load_existing_token(self, mocker: MockerFixture) -> None:
        """Load existing token file and retrieve correct data structure."""
        test_data = {"token": "test", "namespaces": {}, "email": "test@example.com"}
        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data=json.dumps(test_data))
        )
        mocker.patch("os.path.exists", return_value=True)

        result = load_token()

        mock_open.assert_called_once()
        assert result == test_data

    def test_delete_existing_token(self, mocker: MockerFixture) -> None:
        """Delete existing token file successfully."""
        mock_exists = mocker.patch("os.path.exists", return_value=True)
        mock_remove = mocker.patch("os.remove")

        delete_token()

        mock_exists.assert_called_once_with(TOKEN_FILE)
        mock_remove.assert_called_once_with(TOKEN_FILE)

    def test_clean_namespaces_removes_at_symbols(self) -> None:
        """Clean namespaces by removing @ symbols from default and groups values."""
        namespaces = {"default": "@test-namespace", "groups": ["@group1", "@group2"]}

        result = clean_namespaces(namespaces)

        assert result["default"] == "test-namespace"
        assert result["groups"] == ["group1", "group2"]

    def test_load_namespaces_from_token(self, mocker: MockerFixture) -> None:
        """Load default namespace from existing token file."""
        test_data = {"namespaces": {"default": "test-namespace"}}
        mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(test_data)))
        mocker.patch("os.path.exists", return_value=True)

        result = load_namespaces()

        assert result == "test-namespace"

    def test_load_token_nonexistent_file(self, mocker: MockerFixture) -> None:
        """Attempt to load token when file doesn't exist returns empty dict."""
        mocker.patch("os.path.exists", return_value=False)

        result = load_token()

        assert result == {}

    def test_delete_nonexistent_token(self, mocker: MockerFixture) -> None:
        """Delete token when file doesn't exist has no effect."""
        mock_exists = mocker.patch("os.path.exists", return_value=False)
        mock_remove = mocker.patch("os.remove")

        delete_token()

        mock_exists.assert_called_once_with(TOKEN_FILE)
        mock_remove.assert_not_called()

    def test_clean_namespaces_missing_keys(self) -> None:
        """Clean namespaces with missing default or groups keys."""
        namespaces = {"other_key": "value"}

        result = clean_namespaces(namespaces)

        assert result == namespaces
        assert "default" not in result
        assert "groups" not in result

    def test_handle_permission_errors(self, mocker: MockerFixture) -> None:
        """Handle permission errors when saving/loading/deleting token file."""
        mocker.patch("builtins.open", side_effect=PermissionError)
        mocker.patch("os.path.exists", return_value=True)

        with pytest.raises(PermissionError):
            save_token("test", {}, "test@example.com")

        with pytest.raises(PermissionError):
            load_token()


class TestAuthCommands:
    """Test cases for the authentication CLI commands."""

    def test_signup_success_with_valid_credentials(self, mocker: MockerFixture) -> None:
        """Successful user signup with valid username, email and password."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.signup")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")
        mock_click = mocker.patch("click.secho")

        mock_registry.return_value = {
            "token": "test_token",
            "namespaces": {"default": "testuser", "groups": ["testuser"]},
            "email": "testuser@test.com",
        }

        runner = CliRunner()
        result = runner.invoke(
            signup, input="testuser\ntestuser@test.com\npassword\npassword\n"
        )

        assert result.exit_code == 0
        mock_registry.assert_called_once_with(
            "testuser", "testuser@test.com", "password"
        )
        mock_save.assert_called_once()
        mock_click.assert_called_with(
            "Signup successful! Token saved.", fg="green", bold=True
        )

    def test_login_success_with_email(self, mocker: MockerFixture) -> None:
        """Successful user login with email and password."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.login")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")
        mock_click = mocker.patch("click.secho")

        mock_registry.return_value = {
            "token": "test_token",
            "namespaces": {"default": "testuser", "groups": ["testuser"]},
            "email": "testuser@test.com",
        }

        runner = CliRunner()
        result = runner.invoke(login, input="testuser@test.com\npassword\n")

        assert result.exit_code == 0
        mock_registry.assert_called_once_with("testuser@test.com", "password")
        mock_save.assert_called_once()
        mock_click.assert_called_with(
            "Login successful! Token saved.", fg="green", bold=True
        )

    def test_login_success_with_username(self, mocker: MockerFixture) -> None:
        """Successful user login with username and password."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.login")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")
        mock_click = mocker.patch("click.secho")

        mock_registry.return_value = {
            "token": "test_token",
            "namespaces": {"default": "testuser", "groups": ["testuser"]},
            "email": "testuser@test.com",
        }

        runner = CliRunner()
        result = runner.invoke(login, input="testuser\npassword\n")

        assert result.exit_code == 0
        mock_registry.assert_called_once_with("testuser", "password")
        mock_save.assert_called_once()
        mock_click.assert_called_with(
            "Login successful! Token saved.", fg="green", bold=True
        )

    def test_logout_success(self, mocker: MockerFixture) -> None:
        """Successful user logout and token deletion."""
        mock_delete = mocker.patch("jvcli.commands.auth.delete_token")
        mock_click = mocker.patch("click.secho")

        runner = CliRunner()
        result = runner.invoke(logout)

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_click.assert_called_with(
            "You have been logged out.", fg="green", bold=True
        )

    def test_token_saved_after_signup(self, mocker: MockerFixture) -> None:
        """Token is correctly saved after successful signup."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.signup")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")

        test_data = {
            "token": "test_token",
            "namespaces": {"default": "test", "groups": ["test"]},
            "email": "testuser@test.com",
        }
        mock_registry.return_value = test_data

        runner = CliRunner()
        runner.invoke(signup, input="testuser\ntestuser@test.com\npassword\npassword\n")

        mock_save.assert_called_once_with(
            test_data["token"], test_data["namespaces"], test_data["email"]
        )

    def test_token_saved_after_login(self, mocker: MockerFixture) -> None:
        """Token is correctly saved after successful login."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.login")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")

        test_data = {
            "token": "test_token",
            "namespaces": {"default": "test", "groups": ["test"]},
            "email": "testuser@test.com",
        }
        mock_registry.return_value = test_data

        runner = CliRunner()
        runner.invoke(login, input="testuser@test.com\npassword\n")

        mock_save.assert_called_once_with(
            test_data["token"], test_data["namespaces"], test_data["email"]
        )

    def test_signup_invalid_email(self, mocker: MockerFixture) -> None:
        """Signup with invalid email format."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.signup")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")

        mock_registry.return_value = {}

        runner = CliRunner()
        result = runner.invoke(
            signup, input="testuser\ninvalid-email\npassword\npassword\n"
        )

        assert result.exit_code == 0
        mock_save.assert_not_called()

    def test_login_nonexistent_user(self, mocker: MockerFixture) -> None:
        """Login with non-existent user credentials."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.login")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")

        mock_registry.return_value = {}

        runner = CliRunner()
        result = runner.invoke(login, input="nonexistent@test.com\npassword\n")

        assert result.exit_code == 0
        mock_save.assert_not_called()

    def test_login_incorrect_password(self, mocker: MockerFixture) -> None:
        """Login with incorrect password."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.login")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")

        mock_registry.return_value = {}

        runner = CliRunner()
        result = runner.invoke(login, input="test@test.com\nwrongpassword\n")

        assert result.exit_code == 0
        mock_save.assert_not_called()

    def test_logout_no_token(self, mocker: MockerFixture) -> None:
        """Logout when no token exists."""
        mock_delete = mocker.patch("jvcli.auth.delete_token")
        mock_click = mocker.patch("click.secho")

        mock_delete.side_effect = FileNotFoundError

        runner = CliRunner()
        result = runner.invoke(logout)

        assert result.exit_code == 0
        mock_click.assert_called_with(
            "You have been logged out.", fg="green", bold=True
        )

    def test_signup_existing_user(self, mocker: MockerFixture) -> None:
        """Signup when user already exists."""
        mock_registry = mocker.patch("jvcli.api.RegistryAPI.signup")
        mock_save = mocker.patch("jvcli.commands.auth.save_token")
        mock_registry.return_value = {}

        runner = CliRunner()
        result = runner.invoke(
            signup, input="existinguser\ntest@test.com\npassword\npassword\n"
        )

        assert result.exit_code == 0
        mock_save.assert_not_called()
