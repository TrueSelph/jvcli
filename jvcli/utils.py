"""Utility functions for the Jivas Package Repository CLI tool."""

import os
import re
import tarfile

import click
import yaml
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from jvcli import __supported__jivas__versions__
from jvcli.api import RegistryAPI
from jvcli.auth import load_token

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def validate_snake_case(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate that the input is in snake_case."""
    if not re.match(r"^[a-z0-9_]+$", value):
        raise click.BadParameter(
            "must be snake_case (lowercase letters, numbers, and underscores only)."
        )
    return value


def validate_name(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate that the input only contains lowercase letters and numbers. Used for validating names."""
    if not re.match(r"^[a-z0-9]+$", value):
        raise click.BadParameter("must be lowercase letters and numbers only.")
    return value


def validate_yaml_format(info_data: dict, type: str, version: str = "latest") -> bool:
    """Validate if the info.yaml data matches the corresponding version template."""
    if version == "latest":
        version = max(__supported__jivas__versions__)

    if type == "action" or type.endswith("action"):
        template_path = os.path.join(TEMPLATES_DIR, version, "action_info.yaml")

    if type == "daf" or type == "agent":
        template_path = os.path.join(TEMPLATES_DIR, version, "agent_info.yaml")

    if not os.path.exists(template_path):
        click.secho(f"Template for version {version} not found.", fg="red")
        return False

    # Load template
    with open(template_path, "r") as template_file:
        # Fill placeholders to avoid YAML error
        template_content = template_file.read().format(
            dict.fromkeys(info_data.keys(), "")
        )
        template_data = yaml.safe_load(template_content)

    # Compare keys
    if set(info_data.keys()) != set(template_data.keys()):
        missing_keys = set(template_data.keys()) - set(info_data.keys())
        extra_keys = set(info_data.keys()) - set(template_data.keys())

        if extra_keys:
            click.secho(
                f"Warning: Extra keys: {extra_keys} found in info.yaml, the jivas package repository may ignore them.",
                fg="yellow",
            )

        if missing_keys:
            click.secho(
                f"info.yaml validation failed. Missing keys: {missing_keys}",
                fg="red",
            )
            return False
    return True


def validate_package_name(name: str) -> None:
    """Ensure the package name includes a namespace and matches user access."""
    if "/" not in name:
        raise ValueError(
            f"Package name '{name}' must include a namespace (e.g., 'namespace/action_name')."
        )

    namespace, _ = name.split("/", 1)
    namespaces = load_token().get("namespaces", {}).get("groups", [])
    if namespace not in namespaces:
        raise ValueError(
            f"Namespace '{namespace}' is not accessible to the current user."
        )


def is_version_compatible(version: str, specifiers: str) -> bool:
    """
    Determines if the provided version satisfies the given specifiers or exact version match.

    Args:
    - version (str): The version to be checked. E.g., "2.1.0".
    - specifiers (str): The version specifier set or exact version. E.g., "2.1.0", ">=0.2,<0.3", or "^2.0.0".

    Returns:
    - bool: True if the version satisfies the specifier set or exact match, False otherwise.
    """
    try:
        # Handle edge cases for empty strings or None inputs
        if not version or not specifiers:
            return False

        # Handle exact version equality when no special characters present
        if all(c not in specifiers for c in "<>!=~^*,"):
            return Version(version) == Version(specifiers)

        # Handle tilde (~) syntax, as in npm semver, if used
        if specifiers.startswith("~"):
            base_version = Version(specifiers[1:])
            if base_version.release is None or len(base_version.release) < 2:
                raise InvalidSpecifier(f"Invalid tilde specifier: '{specifiers}'")
            next_minor = base_version.minor + 1
            specifiers = f">={base_version},<{base_version.major}.{next_minor}.0"

        # Explicitly handle caret (^) syntax (npm semver style)
        elif specifiers.startswith("^"):
            base_version = Version(specifiers[1:])
            major, minor, patch = (
                base_version.major,
                base_version.minor,
                base_version.micro,
            )

            if major > 0:
                specifiers = f">={base_version},<{major + 1}.0.0"
            elif major == 0 and minor > 0:
                specifiers = f">={base_version},<0.{minor + 1}.0"
            else:  # major == 0 and minor == 0
                specifiers = f">={base_version},<0.0.{patch + 1}"

        # Finally check using the SpecifierSet
        specifier_set = SpecifierSet(specifiers)
        parsed_version = Version(version)

        return parsed_version in specifier_set

    except (InvalidVersion, InvalidSpecifier, TypeError) as e:
        print(f"Version parsing error: {e}")
        return False


def validate_dependencies(dependencies: dict) -> None:
    """Ensure all dependencies exist in the registry."""
    missing_dependencies = []
    for dep, specifier in dependencies.items():
        if dep == "jivas":
            # Check if the version is in list of supported versions
            def supported(spec: str) -> bool:
                return any(
                    is_version_compatible(version, spec)
                    for version in __supported__jivas__versions__
                )

            if not supported(specifier):
                missing_dependencies.append(f"{dep} {specifier}")
        elif dep == "actions":
            # Check if action exists in the registry
            for name, spec in specifier.items():
                package = RegistryAPI.download_package(
                    name=name, version=spec, suppress_error=True
                )

                if not package:
                    missing_dependencies.append(f"{dep} {specifier}")
        elif dep == "pip":
            # TODO: Add support for pip dependencies
            continue
        else:
            raise ValueError(f"Unknown dependency type: {dep}")

    if missing_dependencies:
        raise ValueError(f"Dependencies not found in registry: {missing_dependencies}")


def compress_package_to_tgz(source_path: str, output_filename: str) -> str:
    """
    Compress the action folder into a .tgz file with the required structure,
    excluding the __jac_gen__ folder.

    Args:
        source_path (str): Path to the action directory.
        output_filename (str): Desired name of the output .tgz file.

    Returns:
        str: Path to the .tgz file.
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        for root, dirs, files in os.walk(source_path):
            # Exclude the __jac_gen__ folder
            if "__jac_gen__" in dirs:
                dirs.remove("__jac_gen__")
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source_path)
                tar.add(file_path, arcname=arcname)
    return output_filename
