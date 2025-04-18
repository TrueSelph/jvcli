"""Initialize agents in the Jivas system."""

import os
import sys

import click
import requests

from jvcli.auth import login_jivas
from jvcli.utils import is_server_running


@click.command()
def initagents() -> None:
    """
    Initialize agents in the Jivas system.

    Usage:
        jvcli initagents
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

    # Initialize agents
    try:
        response = requests.post(
            f"{os.environ['JIVAS_BASE_URL']}/walker/init_agents",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        if response.status_code == 200:
            data = response.json()
            click.secho(f"Successfully initialized agents: {data}", fg="green")
        else:
            click.secho("Failed to initialize agents", fg="red")
            sys.exit(1)
    except requests.RequestException as e:
        click.secho(f"Error during request: {e}", fg="red")
        sys.exit(1)
