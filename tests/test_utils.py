"""Test suite for util functions in jvcli.utils."""

import os
import tarfile
import tempfile

import click
import pytest
from pytest_mock import MockerFixture

from jvcli.utils import (
    TEMPLATES_DIR,
    compress_package_to_tgz,
    is_version_compatible,
    validate_dependencies,
    validate_name,
    validate_package_name,
    validate_snake_case,
    validate_yaml_format,
)


class TestUtilsFullCoverage:
    """Comprehensive test cases for jvcli/utils.py with edge cases and regression coverage."""

    # ---------- validate_snake_case ----------
    @pytest.mark.parametrize(
        "value",
        [
            "snake_case",
            "snake123_case4",
            "snake_123",
            "a",
            "z",
            "1",
            "__",  # underscores allowed
            "snake_case_",
        ],
    )
    def test_validate_snake_case_accepts_valid_strings(self, value: str) -> None:
        """Test validate_snake_case accepts valid snake_case inputs."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        assert validate_snake_case(ctx, param, value) == value

    @pytest.mark.parametrize(
        "value",
        [
            "Snake_Case",
            "snake-case",
            "snake@case",
            "snake.case",
            "snakeCase",
            "-snake_case",
            "",
            " ",  # space
            "*",
            "SNAKE_CASE",
            "snake_case!",
        ],
    )
    def test_validate_snake_case_rejects_invalid_strings(self, value: str) -> None:
        """Test validate_snake_case rejects invalid snake_case-like inputs."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        with pytest.raises(click.BadParameter):
            validate_snake_case(ctx, param, value)

    # ---------- validate_name ----------
    @pytest.mark.parametrize("value", ["test123", "abc", "123abc", "a", "z", "123"])
    def test_validate_name_accepts_valid_strings(self, value: str) -> None:
        """Test validate_name accepts simple alphanumeric names."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        assert validate_name(ctx, param, value) == value

    @pytest.mark.parametrize(
        "value",
        [
            "Test123",
            "abc_123",
            "test-123",
            "Test",
            "test!",
            "abc test",
            "",
            "ABC",
            "abc123_",
            "abc-123",
        ],
    )
    def test_validate_name_rejects_invalid_strings(self, value: str) -> None:
        """Test validate_name rejects names with invalid characters or case."""
        ctx = click.Context(click.Command("test"))
        param = click.Option(["--test"])
        with pytest.raises(click.BadParameter):
            validate_name(ctx, param, value)

    # ---------- validate_yaml_format ----------
    def test_validate_yaml_format_successful_and_file_not_found(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_yaml_format on success and template file not found."""
        mocker.patch(
            "builtins.open", mocker.mock_open(read_data="name: test\nversion: 1.0.0")
        )
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)
        info_data = {"name": "test", "version": "1.0.0"}
        assert validate_yaml_format(info_data, "action") is True

        # Test for template not found
        mocker.patch("os.path.exists", return_value=False)
        mock_secho = mocker.patch("click.secho")
        assert validate_yaml_format(info_data, "action", "2.0.0") is False
        mock_secho.assert_called_with("Template for version 2.0.0 not found.", fg="red")

    def test_validate_yaml_format_with_extra_and_missing_keys(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_yaml_format with missing and extra keys."""
        # Missing key: Fails, Extra key: Warns but passes
        # --- Missing key case
        mocker.patch("builtins.open", mocker.mock_open(read_data="name: test"))
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)
        mock_secho = mocker.patch("click.secho")
        info_data = {"name": "test"}
        assert validate_yaml_format(info_data, "action") is False
        mock_secho.assert_any_call(
            "info.yaml validation failed. Missing keys: {'version'}", fg="red"
        )

        # --- Extra keys case: Should warn and pass
        mock_secho.reset_mock()
        mocker.patch(
            "builtins.open", mocker.mock_open(read_data="name: test\nversion: 1.0.0")
        )
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)
        info_data = {"name": "test", "version": "1.0.0", "extra": "123"}
        assert validate_yaml_format(info_data, "action") is True
        mock_secho.assert_any_call(
            "Warning: Extra keys: {'extra'} found in info.yaml, the jivas package repository may ignore them.",
            fg="yellow",
        )

    def test_validate_yaml_format_empty_info_and_template(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_yaml_format with blank info and blank or non-blank template."""
        # Both empty = should succeed
        mocker.patch("builtins.open", mocker.mock_open(read_data=""))
        mocker.patch("yaml.safe_load", return_value={})
        mocker.patch("os.path.exists", return_value=True)
        assert validate_yaml_format({}, "action") is True

        # info_data empty, template with keys (missing keys -> fail)
        mocker.patch("builtins.open", mocker.mock_open(read_data="name: \nversion: "))
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)
        assert validate_yaml_format({}, "action") is False

    def test_validate_yaml_format_handles_yaml_error(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_yaml_format raises on yaml.safe_load failure."""
        mocker.patch("builtins.open", mocker.mock_open(read_data=":"), create=True)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("yaml.safe_load", side_effect=ValueError("YAML fail"))
        info_data = {"name": "test", "version": "1.0.0"}
        with pytest.raises(ValueError, match="YAML fail"):
            validate_yaml_format(info_data, "action")

    # ---------- validate_package_name ----------
    @pytest.mark.parametrize(
        "token, name",
        [
            ({"namespaces": {"groups": ["ns"]}}, "ns/myaction"),
            ({"namespaces": {"groups": ["ns1", "ns2"]}}, "ns2/a"),
        ],
    )
    def test_validate_package_name_accepts_valid(
        self, mocker: MockerFixture, token: dict, name: str
    ) -> None:
        """Test validate_package_name accepts valid namespace prefixes."""
        mocker.patch("jvcli.utils.load_token", return_value=token)
        validate_package_name(name)

    @pytest.mark.parametrize(
        "token, name",
        [
            ({"namespaces": {"groups": ["ns"]}}, "other/myaction"),
            ({"namespaces": {"groups": ["ns"]}}, "myaction"),
            ({"namespaces": {"groups": []}}, "ns/myaction"),
        ],
    )
    def test_validate_package_name_rejects_invalid(
        self, mocker: MockerFixture, token: dict, name: str
    ) -> None:
        """Test validate_package_name rejects on invalid/unauthorized namespaces."""
        mocker.patch("jvcli.utils.load_token", return_value=token)
        with pytest.raises(ValueError):
            validate_package_name(name)

    def test_validate_package_name_trailing_slash_or_extra_slash(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_package_name with trailing/extra slashes and empty namespace."""
        mocker.patch(
            "jvcli.utils.load_token", return_value={"namespaces": {"groups": ["ns"]}}
        )
        # Multiple slashes allowed, splits at first
        validate_package_name("ns/sub/pack")
        # Fails if empty namespace
        with pytest.raises(ValueError):
            validate_package_name("/package")

    # ---------- is_version_compatible ----------
    @pytest.mark.parametrize(
        "version, spec, want",
        [
            ("1.0.0", "1.0.0", True),
            ("2.1.0", ">=2.0.0,<3.0.0", True),
            ("1.0.0", "^1.0.0", True),
            ("1.2.3", "~1.2.0", True),
            ("", "1.0.0", False),
            ("1.0.0", "", False),
            (None, "1.0.0", False),
            ("1.0.0", None, False),
            ("invalid", "1.0.0", False),
            ("1.0.0", "invalid", False),
            ("1.0", ">=invalid", False),
            ("1.3.0", "~1.2.0", False),
            ("2.0.0", "^1.2.0", False),
            ("0.3.0", "^0.2.0", False),
        ],
    )
    def test_is_version_compatible_general(
        self, version: str, spec: str, want: bool
    ) -> None:
        """Test is_version_compatible for various version and spec combinations."""
        assert is_version_compatible(version, spec) is want

    def test_is_version_compatible_pre_release(self) -> None:
        """Test is_version_compatible with pre-release versions."""
        assert is_version_compatible("1.0.0-alpha", ">=1.0.0-alpha,<2.0.0")
        assert not is_version_compatible("1.0.0-alpha", ">=1.0.0,<2.0.0")
        assert is_version_compatible("1.0.0-beta", "^1.0.0-alpha")
        assert is_version_compatible("1.0.0-alpha", "1.0.0-alpha")
        assert not is_version_compatible("1.0.0-alpha", "1.0.0-beta")

    # ---------- compress_package_to_tgz ----------
    def test_compress_package_to_tgz_includes_and_excludes(self) -> None:
        """Test compress_package_to_tgz includes and excludes proper files."""
        with tempfile.TemporaryDirectory() as source_path:
            os.makedirs(os.path.join(source_path, "subdir"), exist_ok=True)
            with open(os.path.join(source_path, "file1.txt"), "w") as f:
                f.write("file1")
            with open(os.path.join(source_path, "subdir", "f2.txt"), "w") as f:
                f.write("file2")
            os.makedirs(os.path.join(source_path, "__jac_gen__"))
            os.makedirs(os.path.join(source_path, "__pycache__"))

            out_tgz = os.path.join(source_path, "output.tgz")
            out = compress_package_to_tgz(source_path, out_tgz)
            assert os.path.exists(out)
            with tarfile.open(out, "r:gz") as tar:
                names = tar.getnames()
            assert "file1.txt" in names
            assert "subdir/f2.txt" in names
            assert "__jac_gen__" not in names
            assert "__pycache__" not in names

    def test_compress_package_to_tgz_permission_error(
        self, mocker: MockerFixture
    ) -> None:
        """Test compress_package_to_tgz PermissionError during archiving."""
        mocker.patch("tarfile.open", side_effect=PermissionError("Denied"))
        with pytest.raises(PermissionError):
            compress_package_to_tgz("dummy_dir", "out.tgz")

    # ---------- validate_dependencies ----------
    def test_validate_dependencies_all_ok_and_jivas_not_found(
        self, mocker: MockerFixture
    ) -> None:
        """Test validate_dependencies: compatible/incompatible jivas version."""
        # Compatible jivas version
        dependencies = {"jivas": ">=2.0.0,<3.0.0"}
        validate_dependencies(dependencies)
        # Incompatible jivas version: raises
        bad = {"jivas": ">=99.0.0"}
        with pytest.raises(ValueError):
            validate_dependencies(bad)

    def test_validate_dependencies_empty_dict(self) -> None:
        """Test validate_dependencies with empty dependency dict."""
        validate_dependencies({})

    def test_validate_dependencies_actions(self, mocker: MockerFixture) -> None:
        """Test validate_dependencies for actions dependencies."""
        mock_api = mocker.patch(
            "jvcli.api.RegistryAPI.download_package", return_value={"file": 1}
        )
        dependencies = {"actions": {"a": "^1.0.0", "b": ">=2.0.0"}}
        validate_dependencies(dependencies)
        assert mock_api.call_count == 2

    def test_validate_dependencies_actions_missing(self, mocker: MockerFixture) -> None:
        """Test validate_dependencies for missing action."""
        mocker.patch("jvcli.api.RegistryAPI.download_package", return_value=None)
        dependencies = {"actions": {"a": "^1.0.0"}}
        with pytest.raises(
            ValueError,
            match=r"Dependencies not found in registry: \[\"actions \{'a': '\^1.0.0'\}\"\]",
        ):
            validate_dependencies(dependencies)

    def test_validate_dependencies_pip_and_unknown(self) -> None:
        """Test validate_dependencies for pip and unknown dep types."""
        # pip: no error
        validate_dependencies({"pip": ">=1.0.0"})
        # unknown: error
        with pytest.raises(ValueError, match="Unknown dependency type: unknown"):
            validate_dependencies({"unknown": ">=1.0.0"})

    def test_validate_dependencies_actions_not_dict(self) -> None:
        """Test validate_dependencies for non-dict actions value."""
        # If actions dep value is not dict, expect ValueError from RegistryAPI
        with pytest.raises(AttributeError):  # Will try .items() on non-dict
            validate_dependencies({"actions": "2.0.0"})

    # ---------- Extra: YAML validation for 'daf' and 'agent' types ----------
    @pytest.mark.parametrize("type_key", ["daf", "agent"])
    def test_validate_yaml_format_for_daf_and_agent(
        self, mocker: MockerFixture, type_key: str
    ) -> None:
        """Test validate_yaml_format works for 'daf' and 'agent' type_key."""
        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data="name: test\nversion: 1.0.0")
        )
        mocker.patch("yaml.safe_load", return_value={"name": "", "version": ""})
        mocker.patch("os.path.exists", return_value=True)
        info_data = {"name": "test", "version": "1.0.0"}
        assert validate_yaml_format(info_data, type_key, "2.0.0") is True
        mock_open.assert_called_once_with(
            os.path.join(TEMPLATES_DIR, "2.0.0", "agent_info.yaml"), "r"
        )
