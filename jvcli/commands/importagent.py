"""Command to import an agent from a DAF package."""

import json
import os
import sys

import click
import requests

from jvcli.auth import login_jivas
from jvcli.utils import is_server_running


@click.command()
@click.argument("agent_name")
@click.argument("version", required=False)
def importagent(agent_name: str, version: str) -> None:
    """
    Import an agent from a DAF package.

    Usage:
        jvcli importagent <agent_name> [--version <jivas_version>]
    """

    # Check if server is running
    if not is_server_running():
        click.secho("Server is not running. Please start the server first.", fg="red")
        sys.exit(1)

    # Login to Jivas
    token = login_jivas()
    if not token:
        click.secho("Failed to login to Jivas.", fg="red")
        sys.exit(1)
    click.secho("Logged in to Jivas successfully.", fg="green")

    # Check if version is provided
    if not version:
        version = "latest"

    try:
        response = requests.post(
            f"{os.environ.get('JIVAS_BASE_URL', 'http://localhost:8000')}/walker/import_agent",
            json={"daf_name": agent_name, "daf_version": version},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        if response.status_code == 200:
            try:
                data = response.json()
                agent_id = data.get("id")
                if agent_id:
                    click.secho(
                        f"Successfully imported agent. Agent ID: {agent_id}", fg="green"
                    )
                else:
                    click.secho(
                        "Agent imported but no ID was returned in the response",
                        fg="yellow",
                    )
            except json.JSONDecodeError:
                click.secho("Invalid JSON response from server", fg="red")
                sys.exit(1)
        else:
            click.secho(
                f"Failed to import agent. Status: {response.status_code}", fg="red"
            )
            click.echo(response.text)
            sys.exit(1)
    except requests.RequestException as e:
        click.secho(f"Request failed: {e}", fg="red")
        sys.exit(1)
