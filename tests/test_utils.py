"""Tests for the utility functions in jvcli/utils.py"""

import os
import tarfile
import tempfile

import click
import pytest
from pytest_mock import MockerFixture

from jvcli.utils import (
    compress_package_to_tgz,
    is_version_compatible,
    validate_dependencies,
    validate_name,
    validate_package_name,
    validate_snake_case,
    validate_yaml_format,
)


class TestUtils:
    """Test cases for the utility functions."""

    def test_validate_snake_case_accepts_valid_strings(self) -> None:
        """validate_snake_case accepts valid snake_case strings with lowercase letters, numbers and underscores."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        valid_strings = ["snake_case", "snake123_case", "snake_123"]

        for test_str in valid_strings:
            result = validate_snake_case(ctx, param, test_str)
            assert result == test_str

    def test_validate_name_accepts_valid_strings(self) -> None:
        """validate_name accepts strings with only lowercase letters and numbers."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        valid_strings = ["test123", "abc", "123abc"]

        for test_str in valid_strings:
            result = validate_name(ctx, param, test_str)
            assert result == test_str

    def test_validate_yaml_format_with_valid_data(self, mocker: MockerFixture) -> None:
        """validate_yaml_format successfully validates info.yaml against corresponding template."""
        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data="name: test\nversion: 1.0.0")
        )
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)

        info_data = {"name": "test", "version": "1.0.0"}

        validate_yaml_format(info_data, "action")
        mock_open.assert_called_once()

    def test_validate_package_name_with_valid_namespace(
        self, mocker: MockerFixture
    ) -> None:
        """validate_package_name verifies namespace format and user access."""
        mocker.patch(
            "jvcli.utils.load_token",
            return_value={"namespaces": {"groups": ["test-ns"]}},
        )

        validate_package_name("test-ns/package-name")

    def test_is_version_compatible_with_exact_match(self) -> None:
        """is_version_compatible correctly handles exact version matches and version ranges."""
        assert is_version_compatible("1.0.0", "1.0.0") is True
        assert is_version_compatible("2.1.0", ">=2.0.0,<3.0.0") is True
        assert is_version_compatible("1.0.0", "^1.0.0") is True

    def test_validate_snake_case_rejects_invalid_strings(self) -> None:
        """validate_snake_case rejects strings with uppercase letters or special characters."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        invalid_strings = ["Snake_Case", "snake-case", "snake@case"]

        for test_str in invalid_strings:
            with pytest.raises(click.BadParameter):
                validate_snake_case(ctx, param, test_str)

    def test_validate_name_rejects_invalid_strings(self) -> None:
        """validate_name rejects strings with uppercase letters or special characters."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        invalid_strings = ["Test123", "abc_123", "test-123"]

        for test_str in invalid_strings:
            with pytest.raises(click.BadParameter):
                validate_name(ctx, param, test_str)

    def test_validate_yaml_format_with_invalid_keys(
        self, mocker: MockerFixture
    ) -> None:
        """validate_yaml_format handles missing or extra keys in info.yaml."""
        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data="name: test\nversion: 1.0.0")
        )
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)

        info_data = {"name": "test", "invalid_key": "value"}
        with pytest.raises(ValueError):
            validate_yaml_format(info_data, "action")

        mock_open.assert_called_once()

    def test_validate_package_name_with_invalid_namespace(
        self, mocker: MockerFixture
    ) -> None:
        """validate_package_name fails for missing namespace or unauthorized access."""
        mocker.patch(
            "jvcli.utils.load_token",
            return_value={"namespaces": {"groups": ["test-ns"]}},
        )

        with pytest.raises(ValueError):
            validate_package_name("invalid-ns/package-name")

        with pytest.raises(ValueError):
            validate_package_name("package-name")

    def test_is_version_compatible_with_invalid_versions(self) -> None:
        """is_version_compatible handles malformed version strings and specifiers."""
        assert is_version_compatible("invalid", "1.0.0") is False
        assert is_version_compatible("1.0.0", "invalid") is False
        assert is_version_compatible("1.0", ">=invalid") is False

    def test_compress_package_to_tgz(self) -> None:
        """Test that compress_package_to_tgz correctly creates a .tgz archive, excluding unwanted folders."""

        # Create a temporary directory to simulate the source path
        with tempfile.TemporaryDirectory() as source_path:
            # Create some test files
            os.makedirs(os.path.join(source_path, "subdir"), exist_ok=True)
            with open(os.path.join(source_path, "file1.txt"), "w") as f:
                f.write("test file 1")
            with open(os.path.join(source_path, "subdir", "file2.txt"), "w") as f:
                f.write("test file 2")

            # Create unwanted directories
            os.makedirs(os.path.join(source_path, "__jac_gen__"), exist_ok=True)
            os.makedirs(os.path.join(source_path, "__pycache__"), exist_ok=True)

            # Define output .tgz filename
            output_filename = os.path.join(source_path, "output.tgz")

            # Act: Call the function
            compressed_file = compress_package_to_tgz(source_path, output_filename)

            # Assert: Ensure the output file exists
            assert os.path.exists(compressed_file), "The .tgz archive was not created."

            # Extract the .tgz and check contents
            with tarfile.open(compressed_file, "r:gz") as tar:
                archive_files = tar.getnames()  # List of files inside .tgz

            # Ensure included files are present
            assert "file1.txt" in archive_files
            assert "subdir/file2.txt" in archive_files

            # Ensure excluded directories are NOT present
            assert "__jac_gen__" not in archive_files
            assert "__pycache__" not in archive_files

    def test_is_version_compatible_with_tilde_and_caret_specifiers(self) -> None:
        """is_version_compatible processes tilde (~) and caret (^) version specifiers."""
        # Test cases for tilde (~) specifier
        assert is_version_compatible("2.1.0", "~2.1.0") is True
        assert is_version_compatible("2.1.5", "~2.1.0") is True
        assert is_version_compatible("2.2.0", "~2.1.0") is False

        # Test cases for caret (^) specifier
        assert is_version_compatible("2.1.0", "^2.0.0") is True
        assert is_version_compatible("3.0.0", "^2.0.0") is False
        assert is_version_compatible("0.2.5", "^0.2.0") is True
        assert is_version_compatible("0.3.0", "^0.2.0") is False

    def test_compress_package_to_tgz_preserves_structure_and_permissions(
        self, mocker: MockerFixture
    ) -> None:
        """compress_package_to_tgz preserves file structure and permissions."""

        # Setup
        source_path = "test_source"
        output_filename = "test_output.tgz"
        os.makedirs(source_path, exist_ok=True)
        file_structure = {
            "file1.txt": "content1",
            "dir1/file2.txt": "content2",
            "__jac_gen__/file3.txt": "content3",
            "__pycache__/file4.txt": "content4",
        }

        # Create files and directories
        for path, content in file_structure.items():
            full_path = os.path.join(source_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        # Mock tarfile.open to avoid actual file creation
        mock_tarfile_open = mocker.patch("tarfile.open", autospec=True)
        mock_tar = mock_tarfile_open.return_value.__enter__.return_value

        # Execute
        result = compress_package_to_tgz(source_path, output_filename)

        # Verify
        assert result == output_filename
        expected_calls = [
            mocker.call(os.path.join(source_path, "file1.txt"), arcname="file1.txt"),
            mocker.call(
                os.path.join(source_path, "dir1/file2.txt"), arcname="dir1/file2.txt"
            ),
        ]
        mock_tar.add.assert_has_calls(expected_calls, any_order=True)
        assert not any(
            "__jac_gen__" in call[0][0] for call in mock_tar.add.call_args_list
        )
        assert not any(
            "__pycache__" in call[0][0] for call in mock_tar.add.call_args_list
        )

        # Cleanup
        for path in file_structure.keys():
            os.remove(os.path.join(source_path, path))
        os.removedirs(os.path.join(source_path, "dir1"))

    def test_validate_dependencies_jivas_version_compatibility(
        self, mocker: MockerFixture
    ) -> None:
        """validate_dependencies verifies jivas version compatibility."""
        # Mock the RegistryAPI.download_package method
        mock_download_package = mocker.patch(
            "jvcli.api.RegistryAPI.download_package", return_value={}
        )

        # Mock the version of jivas
        mocker.patch("jvcli.__version__", "2.1.0")

        # Define dependencies with jivas version specifier
        dependencies = {"jivas": ">=2.0.0,<3.0.0", "other_dep": ">=1.0.0"}

        # Call validate_dependencies and expect no exception for compatible jivas version
        try:
            validate_dependencies(dependencies)
        except ValueError as e:
            pytest.fail(f"validate_dependencies raised ValueError unexpectedly: {e}")

        # Assert that download_package was called for non-jivas dependencies
        mock_download_package.assert_called_once_with(
            name="other_dep", version=">=1.0.0", suppress_error=True
        )
