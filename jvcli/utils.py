"""Utility functions for the Jivas Package Repository CLI tool."""

import os
import re
import tarfile

import click
import yaml
from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version

from jvcli import __version__ as version
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


def validate_yaml_format(info_data: dict, type: str) -> None:
    """Validate if the info.yaml data matches the corresponding version template."""
    if type == "action" or type.endswith("action"):
        template_path = os.path.join(TEMPLATES_DIR, version, "action_info.yaml")

    if type == "daf" or type == "agent":
        template_path = os.path.join(TEMPLATES_DIR, version, "agent_info.yaml")

    if not os.path.exists(template_path):
        raise ValueError(f"Template for version {version} not found.")

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
        raise ValueError(
            f"info.yaml validation failed. "
            f"Missing keys: {missing_keys}, Extra keys: {extra_keys}"
        )


def validate_package_name(name: str) -> None:
    """Ensure the package name includes a namespace and matches user access."""
    if "/" not in name:
        raise ValueError(
            f"Package name '{name}' must include a namespace (e.g., 'namespace/action_name')."
        )

    namespace, _ = name.split("/", 1)
    namespaces = load_token().get("namespaces", {}).get("groups", [])
    click.secho(f"Valid namespaces: {namespaces}", fg="yellow")
    if namespace not in namespaces:
        raise ValueError(
            f"Namespace '{namespace}' is not accessible to the current user."
        )


def is_version_compatible(version: str, specifiers: str) -> bool:
    """
    Compares the provided version to a given set of specifications/modifiers or exact version match.

    Args:
    - version (str): The version to be compared. E.g., "2.1.0".
    - specifiers (str): The version specifier set or exact version. E.g., "2.1.0" or ">=0.2,<0.3" or "0.0.1" or "^2.0.0"

    Returns:
    - bool: True if the version satisfies the specifier set or exact match, False otherwise.
    """
    try:
        # Parse the version to check
        version = parse_version(version)

        # Check if specifiers is a simple exact version match
        try:
            exact_version = parse_version(specifiers)
            return version == exact_version
        except Exception:
            # If parsing fails, treat it as a specifier set
            pass

        # Handle "~" shorthand by translating it to a compatible range
        if specifiers.startswith("~"):
            base_version = specifiers[1:]
            parsed_base = parse_version(base_version)
            major = parsed_base.major
            minor = parsed_base.minor
            # Assuming the next release constraint is on minor bump
            upper_bound = f"<{major}.{minor + 1}"
            specifiers = f">={base_version},{upper_bound}"

        # Handle "^" shorthand to translate to a compatible range
        if specifiers.startswith("^"):
            base_version = specifiers[1:]
            parsed_base = parse_version(base_version)
            major = parsed_base.major
            minor = parsed_base.minor
            patch = parsed_base.micro
            if major > 0:
                upper_bound = f"<{major + 1}.0.0"
            elif minor > 0:
                upper_bound = f"<0.{minor + 1}.0"
            else:
                upper_bound = f"<0.0.{patch + 1}"
            specifiers = f">={base_version},{upper_bound}"

        # Create a SpecifierSet with the given specifiers
        spec_set = SpecifierSet(specifiers)

        # Check if the version matches the specifier set
        return version in spec_set

    except Exception as e:
        # Handle exceptions if the inputs are malformed or invalid
        print(f"Error comparing versions: {e}")
        return False


def validate_dependencies(dependencies: dict) -> None:
    """Ensure all dependencies exist in the registry."""
    missing_dependencies = []
    for dep, specifier in dependencies.items():
        if dep == "jivas":
            if not is_version_compatible(version, specifier):
                missing_dependencies.append(f"jivas {specifier}")
            # Exit loop
        else:
            # specifier formatted like ">=0.0.1", "<0.0.2"
            package = RegistryAPI.download_package(
                name=dep, version=specifier, suppress_error=True
            )
            if not package and dep == "jivas":
                missing_dependencies.append(f"{dep} {specifier}")

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
