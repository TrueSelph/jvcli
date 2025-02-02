"""Publish command group for the Jivas Package Repository CLI."""

import os
import tempfile

import click
from pyaml import yaml

from jvcli.api import RegistryAPI
from jvcli.auth import load_token
from jvcli.utils import (
    compress_package_to_tgz,
    validate_dependencies,
    validate_package_name,
    validate_yaml_format,
)


# Main `publish` group command
@click.group()
def publish() -> None:
    """
    Publish resources to the Jivas environment.
    Available subcommands: action, agent.
    """
    pass


@publish.command(name="action")
@click.option(
    "--path",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Path to the directory containing the action to publish.",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private"], case_sensitive=False),
    default="public",
    show_default=True,
    help="Visibility of the published action (public or private).",
)
@click.option(
    "--file-only",
    "-f",
    is_flag=True,
    default=False,
    show_default=True,
    help="Publish the action to the remote registry.",
)
@click.option(
    "--output",
    "-o",
    required=False,
    type=click.Path(exists=True, file_okay=False),
    help="Output path for generated package.",
)
def publish_action(path: str, visibility: str, file_only: bool, output: str) -> None:
    """Publish an action to the Jivas environment."""
    _publish_common(path, visibility, file_only, output, "action")


@publish.command(name="agent")
@click.option(
    "--path",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Path to the directory containing the agent to publish.",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private"], case_sensitive=False),
    default="private",
    show_default=True,
    help="Visibility of the published agent (public or private).",
)
@click.option(
    "--file-only",
    "-f",
    is_flag=True,
    default=False,
    show_default=True,
    help="Publish the agent to the remote registry.",
)
@click.option(
    "--output",
    "-o",
    required=False,
    type=click.Path(exists=True, file_okay=False),
    help="Output path for generated package.",
)
def publish_agent(path: str, visibility: str, file_only: bool, output: str) -> None:
    """Publish an agent to the Jivas environment."""
    _publish_common(path, visibility, file_only, output, "agent")


def _publish_common(
    path: str, visibility: str, file_only: bool, output: str, publish_type: str
) -> None:
    token = load_token().get("token")
    if not token:
        click.secho("You need to login first.", fg="red")
        return

    info_path = os.path.join(path, "info.yaml")
    if not os.path.exists(info_path):
        click.secho(
            f"Error: 'info.yaml' not found in the directory '{path}'.", fg="red"
        )
        return

    click.secho(f"Publishing {publish_type} from directory: {path}", fg="yellow")

    with open(info_path, "r") as info_file:
        info_data = yaml.safe_load(info_file)

    try:
        validate_yaml_format(info_data, type=publish_type)
        click.secho("info.yaml validated successfully.", fg="yellow")
    except ValueError as e:
        click.secho(f"Error validating 'info.yaml': {e}", fg="red")
        return

    try:
        package_name = info_data["package"].get("name")
        validate_package_name(package_name)
        click.secho(
            f"Package name '{package_name}' validated successfully.", fg="yellow"
        )
    except ValueError as e:
        click.secho(f"Error validating package name: {e}", fg="red")
        return

    try:
        validate_dependencies(info_data["package"].get("dependencies", {}))
        click.secho("Dependencies validated successfully.", fg="yellow")
    except ValueError as e:
        click.secho(f"Error validating dependencies: {e}", fg="red")
        return

    namespace, name = package_name.split("/", 1)

    if file_only and not output:
        output = "."

    tgz_filename = os.path.join(
        output if output else tempfile.gettempdir(), f"{namespace}_{name}.tar.gz"
    )
    tgz_file_path = compress_package_to_tgz(path, tgz_filename)

    click.secho(f"Compressed {publish_type} to: {tgz_file_path}", fg="yellow")

    if not file_only:
        click.secho(
            f"Publishing {publish_type} with visibility: {visibility}", fg="blue"
        )
        response = RegistryAPI.publish_action(
            tgz_file_path, visibility, token, namespace
        )
        if response:
            click.secho(
                f"{publish_type.capitalize()} published successfully!", fg="green"
            )
