"""Test the client utility functions."""

import base64
import json
from io import BytesIO
from pathlib import Path

import pytest
import yaml
from PIL import Image
from pytest_mock import MockerFixture

from jvcli.client.lib.utils import (
    JIVAS_URL,
    LongStringDumper,
    call_action_walker_exec,
    call_get_action,
    call_import_agent,
    call_list_actions,
    call_list_agents,
    call_update_action,
    decode_base64_image,
    jac_yaml_dumper,
    load_function,
)


class TestClientUtils:
    """Test the client utility functions."""

    def test_load_existing_function(self, tmp_path: Path) -> None:
        """Test loading an existing function from a file."""
        # Create a temporary Python file with a test function
        file_content = """
def test_func(x, y):
    return x + y
"""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(file_content)

        # Load the function
        loaded_func = load_function(str(test_file), "test_func")

        # Test the loaded function
        result = loaded_func(1, 2)
        assert result == 3

        # Test with kwargs
        loaded_func_with_kwargs = load_function(str(test_file), "test_func", x=10)
        result_with_kwargs = loaded_func_with_kwargs(y=5)
        assert result_with_kwargs == 15

    def test_load_function_file_not_found(self, mocker: MockerFixture) -> None:
        """Test load_function raises FileNotFoundError when file path does not exist."""
        # Arrange
        non_existent_file_path = "non_existent_file.py"
        function_name = "dummy_function"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            load_function(non_existent_file_path, function_name)

        assert str(excinfo.value) == f"No file found at {non_existent_file_path}"

    def test_load_function_specification_not_loaded(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test load_function when module specification cannot be loaded."""
        # Create a temporary Python file with a test function
        file_content = """
def dummy_function():
    pass
"""
        test_file = tmp_path / "dummy_path.py"
        test_file.write_text(file_content)

        # Mock spec_from_file_location to return None
        mocker.patch(
            "jvcli.client.lib.utils.spec_from_file_location", return_value=None
        )

        # Attempt to load function and expect ImportError
        with pytest.raises(
            ImportError, match="Could not load specification for module dummy_path"
        ):
            load_function(str(test_file), "dummy_function")

    def test_import_error_when_loading_module(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test ImportError is raised when module cannot be loaded."""
        # Create a temporary Python file with a test function
        file_content = """
def dummy_function():
    pass
"""
        test_file = tmp_path / "dummy_path.py"
        test_file.write_text(file_content)

        # Mock spec_from_file_location to return None
        mock_spec = mocker.MagicMock()
        mock_spec.loader = None
        mocker.patch(
            "jvcli.client.lib.utils.spec_from_file_location", return_value=mock_spec
        )

        # Mock module_from_spec
        mocker.patch("jvcli.client.lib.utils.module_from_spec", return_value=None)

        # Attempt to load function and expect ImportError
        with pytest.raises(ImportError, match="Could not load module dummy_path"):
            load_function(str(test_file), "dummy_function")

    def test_load_function_not_found(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test load_function raises AttributeError when function does not exist."""
        # Create a temporary Python file with a test function
        file_content = """
def dummy_function():
    pass
"""

        test_file = tmp_path / "dummy_path.py"
        test_file.write_text(file_content)

        # Attempt to load function and expect AttributeError
        with pytest.raises(
            AttributeError,
            match=f"Function 'dummy_function2' not found in {str(test_file)}",
        ):
            load_function(str(test_file), "dummy_function2")

    def test_call_list_agents_returns_non_empty_list(
        self, mocker: MockerFixture
    ) -> None:
        """Test call_list_agents returns a non-empty list."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate API response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "reports": [
                {"id": "agent_1", "name": "Agent One"},
                {"id": "agent_2", "name": "Agent Two"},
            ]
        }

        # Call the function
        result = call_list_agents()

        # Assert that the result is a non-empty list
        assert len(result) > 0

    def test_call_list_agents_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_list_agents returns empty list on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_list_agents()

        # Assert that the result is an empty list
        assert result == []

    def test_valid_token_returns_actions(self, mocker: MockerFixture) -> None:
        """Test call_list_actions returns actions when token is valid."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"reports": [["action1", "action2"]]}
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Call function
        result = call_list_actions("test_agent")

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            f"{JIVAS_URL}/walker/list_actions",
            json={"agent_id": "test_agent"},
            headers={"Authorization": "Bearer test_token"},
        )

        # Verify result
        assert result == ["action1", "action2"]

    def test_call_list_actions_empty_result(self, mocker: MockerFixture) -> None:
        """Test call_list_actions returns empty list when no actions are found."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate API response with empty reports
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"reports": []}

        # Call the function
        result = call_list_actions("test_agent")

        # Assert that the result is an empty list
        assert len(result) <= 0

    def test_call_list_actions_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_list_actions returns empty list on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_list_actions("test_agent")

        # Assert that the result is an empty list
        assert result == []

    def test_call_list_actions_exception_handling(self, mocker: MockerFixture) -> None:
        """Test call_list_actions handles exceptions and returns empty list."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to raise an exception
        mocker.patch("requests.post", side_effect=Exception("Test Exception"))

        # Call the function
        result = call_list_actions("test_agent")

        # Verify that the exception was handled and an empty list is returned
        assert result == []

    def test_valid_token_returns_action_data(self, mocker: MockerFixture) -> None:
        """Test call_get_action returns action data when token is valid."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"reports": [{"action": "test_action"}]}
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Call function
        result = call_get_action("test_agent", "test_action")

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            f"{JIVAS_URL}/walker/get_action",
            json={"agent_id": "test_agent", "action_id": "test_action"},
            headers={"Authorization": "Bearer test_token"},
        )

        # Verify result
        assert result == {"action": "test_action"}

    def test_call_get_action_empty_result(self, mocker: MockerFixture) -> None:
        """Test call_get_action returns empty list when no action is found."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate API response with empty reports
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"reports": []}

        # Call the function
        result = call_get_action("test_agent_id", "test_action_id")

        # Assert that the result is an empty list
        assert len(result) <= 0

    def test_call_get_action_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_get_action returns empty list on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_get_action("test_agent_id", "test_action_id")

        # Assert that the result is an empty list
        assert result == []

    def test_call_get_action_exception_handling(self, mocker: MockerFixture) -> None:
        """Test call_get_action handles exceptions and returns empty list."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to raise an exception
        mocker.patch("requests.post", side_effect=Exception("Test Exception"))

        # Call the function
        result = call_get_action("test_agent_id", "test_action_id")

        # Verify that the exception was handled and an empty list is returned
        assert result == []

    def test_valid_token_returns_first_report(self, mocker: MockerFixture) -> None:
        """Test call_update_action returns first report when token is valid."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"reports": [{"result": "test_result"}]}
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Call function
        result = call_update_action("test_agent", "test_action", {"test": "data"})

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            f"{JIVAS_URL}/walker/update_action",
            json={
                "agent_id": "test_agent",
                "action_id": "test_action",
                "action_data": {"test": "data"},
            },
            headers={"Authorization": "Bearer test_token"},
        )

        # Verify result
        assert result == {"result": "test_result"}

    def test_call_update_action_empty_result(self, mocker: MockerFixture) -> None:
        """Test call_update_action returns empty dict when no report is found."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate API response with empty reports
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"reports": []}

        # Call the function
        result = call_update_action("test_agent_id", "test_action_id", {"key": "value"})

        # Assert that the result is an empty dictionary
        assert len(result) <= 0

    def test_call_update_action_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_update_action returns empty dict on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_update_action("test_agent_id", "test_action_id", {"key": "value"})

        # Assert that the result is an empty dict
        assert result == {}

    def test_call_update_action_exception_handling(self, mocker: MockerFixture) -> None:
        """Test call_update_action handles exceptions and returns empty dict."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to raise an exception
        mocker.patch("requests.post", side_effect=Exception("Test Exception"))

        # Call the function
        result = call_update_action("test_agent_id", "test_action_id", {"key": "value"})

        # Verify that the exception was handled and an empty dictionary is returned
        assert result == {}

    def test_valid_walker_execution(self, mocker: MockerFixture) -> None:
        """Test call_action_walker_exec returns results when token is valid."""
        # Mock get_user_info to return valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock successful API response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["result1", "result2"]
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Test parameters
        agent_id = "test_agent"
        module_root = "test_module"
        walker = "test_walker"
        args = {"arg1": "value1"}
        files = [("file1.txt", b"content", "text/plain")]

        # Call function
        result = call_action_walker_exec(agent_id, module_root, walker, args, files)

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            url=f"{JIVAS_URL}/walker/action/walker",
            headers={"Authorization": "Bearer test_token"},
            data={
                "agent_id": agent_id,
                "module_root": module_root,
                "walker": walker,
                "args": json.dumps(args),
            },
            files=[("attachments", ("file1.txt", b"content", "text/plain"))],
        )

        # Verify result
        assert result == ["result1", "result2"]

    def test_call_action_walker_exec_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_action_walker_exec returns empty list on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_action_walker_exec(
            "test_agent_id", "test_module_root", "test_walker"
        )

        # Assert that the result is an empty list
        assert result == []

    def test_call_action_walker_exec_exception_handling(
        self, mocker: MockerFixture
    ) -> None:
        """Test call_action_walker_exec handles exceptions and returns empty list."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to raise an exception
        mocker.patch("requests.post", side_effect=Exception("Test Exception"))

        # Call the function
        result = call_action_walker_exec(
            "test_agent_id", "test_module_root", "test_walker"
        )

        # Verify that the exception was handled and an empty list is returned
        assert result == []

    def test_successful_import_agent_call(self, mocker: MockerFixture) -> None:
        """Test call_import_agent returns agents when token is valid."""
        # Mock get_user_info to return valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock successful API response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["agent1", "agent2"]
        mock_post = mocker.patch("requests.post", return_value=mock_response)

        # Test parameters
        descriptor = "test_descriptor"
        headers = {"Custom-Header": "test-value"}

        # Call function
        result = call_import_agent(descriptor, headers)

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            f"{JIVAS_URL}/walker/import_agent",
            headers={
                "Custom-Header": "test-value",
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={"descriptor": descriptor},
        )

        # Verify result
        assert result == ["agent1", "agent2"]

    def test_call_import_agent_unauthorized(self, mocker: MockerFixture) -> None:
        """Test call_import_agent returns empty list on 401 status code."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to simulate a 401 Unauthorized response
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 401

        # Call the function
        result = call_import_agent("test_descriptor")

        # Assert that the result is an empty list
        assert result == []

    def test_call_import_agent_exception_handling(self, mocker: MockerFixture) -> None:
        """Test call_import_agent handles exceptions and returns empty list."""
        # Mock get_user_info to return a valid token
        mocker.patch(
            "jvcli.client.lib.utils.get_user_info",
            return_value={
                "root_id": "test_root_id",
                "token": "test_token",
                "expiration": "test_expiration",
            },
        )

        # Mock requests.post to raise an exception
        mocker.patch("requests.post", side_effect=Exception("Test Exception"))

        # Call the function
        result = call_import_agent("test_descriptor")

        # Verify that the exception was handled and an empty list is returned
        assert result == []

    def test_decode_valid_base64_to_image(self) -> None:
        """Test decoding a valid base64 string to an image."""
        # Arrange
        # Create a small test image and convert to base64
        test_image = Image.new("RGB", (10, 10), color="red")
        buffer = BytesIO()
        test_image.save(buffer, format="PNG")
        base64_string = base64.b64encode(buffer.getvalue()).decode()

        # Act
        result = decode_base64_image(base64_string)

        # Assert
        assert isinstance(result, Image.Image)
        assert result.size == (10, 10)
        assert result.mode == "RGB"
        # Verify pixel color
        assert result.getpixel((0, 0)) == (255, 0, 0)  # Red color in RGB

    def test_short_string_representation(self) -> None:
        """Test that short strings are represented correctly."""
        data = {"message": "Short string"}
        yaml_output = yaml.dump(data, Dumper=LongStringDumper).strip()

        expected_output = "message: Short string"
        assert yaml_output == expected_output

    def test_long_string_representation(self) -> None:
        """Test that long strings use block style (| or |-)."""
        long_text = "This is a very long string " * 10  # More than 150 chars
        data = {"message": long_text}
        yaml_output = yaml.dump(data, Dumper=LongStringDumper).strip()

        # Ensure it starts with block style and contains the text
        assert yaml_output.startswith("message: |")  # YAML block style
        assert "This is a very long string" in yaml_output  # Ensure text is present
        assert yaml_output.endswith(
            "This is a very long string"
        )  # Ensure it ends correctly

    def test_multiline_string_representation(self) -> None:
        """Test that multiline strings use block style."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        data = {"message": multiline_text}
        yaml_output = yaml.dump(data, Dumper=LongStringDumper).strip()

        # Ensure block style is used
        assert yaml_output.startswith("message: |")

        # Normalize indentation and compare content
        expected_content = "\n".join(
            line.strip() for line in multiline_text.split("\n")
        )
        yaml_content = "\n".join(line.strip() for line in yaml_output.split("\n")[1:])
        assert yaml_content == expected_content

    def test_newline_escapes_are_formatted(self) -> None:
        """Test that escape sequences are properly converted."""
        text_with_escapes = "Line 1\nLine 2\nLine 3\n"
        data = {"message": text_with_escapes}
        yaml_output = yaml.dump(data, Dumper=LongStringDumper).strip()

        # Ensure block style (|) is used
        assert yaml_output.startswith("message: |")

        # Normalize indentation and compare
        expected_content = "\n".join(
            line.strip() for line in text_with_escapes.split("\n") if line
        )
        yaml_lines = yaml_output.split("\n")[1:]  # Skip "message: |"
        yaml_content = "\n".join(line.strip() for line in yaml_lines if line)

        assert yaml_content == expected_content

    def test_basic_yaml_dumping(self) -> None:
        """Test that basic data is correctly dumped to YAML."""
        data = {"key": "value"}
        yaml_output = jac_yaml_dumper(data)

        assert yaml_output.strip() == "key: value"

    def test_multiline_string_block_style(self) -> None:
        """Test that multiline strings use block style (|)."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        data = {"message": multiline_text}
        yaml_output = jac_yaml_dumper(data).strip()

        assert yaml_output.startswith("message: |")

        # Normalize indentation and compare
        expected_content = "\n".join(
            line.strip() for line in multiline_text.split("\n")
        )
        yaml_lines = yaml_output.split("\n")[1:]  # Skip "message: |"
        yaml_content = "\n".join(line.strip() for line in yaml_lines)

        assert yaml_content == expected_content

    def test_long_string_block_style(self) -> None:
        """Test that long strings (over 150 characters) are dumped in block style."""
        long_text = "This is a very long string " * 10  # 240+ chars
        data = {"long_message": long_text}
        yaml_output = jac_yaml_dumper(data).strip()

        assert yaml_output.startswith("long_message: |")

    def test_unicode_handling(self) -> None:
        """Test that unicode characters are preserved."""
        unicode_text = "你好, мир, hello"
        data = {"greeting": unicode_text}
        yaml_output = jac_yaml_dumper(data, allow_unicode=True).strip()

        assert "greeting: 你好, мир, hello" in yaml_output

    def test_sort_keys_option(self) -> None:
        """Test that keys are sorted when sort_keys=True."""
        data = {"b_key": "value2", "a_key": "value1"}
        yaml_output = jac_yaml_dumper(data, sort_keys=True).strip()

        assert yaml_output.startswith("a_key: value1\nb_key: value2")

    def test_flow_style(self) -> None:
        """Test that default_flow_style=True results in inline formatting."""
        data = {"items": ["apple", "banana", "cherry"]}
        yaml_output = jac_yaml_dumper(data, default_flow_style=True).strip()

        # Adjust expectation to match PyYAML's default behavior
        assert yaml_output == "{items: [apple, banana, cherry]}"
