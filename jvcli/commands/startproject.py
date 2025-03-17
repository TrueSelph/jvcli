"""Start project command."""

import os

import click

from jvcli import __supported__jivas__versions__
from jvcli.utils import TEMPLATES_DIR


@click.command()
@click.argument("project_name")
@click.option(
    "--version",
    default=max(__supported__jivas__versions__),
    show_default=True,
    help="Jivas project version to use for scaffolding.",
)
def startproject(project_name: str, version: str) -> None:
    """
    Initialize a new Jivas project with the necessary structure.

    Usage:
        jvcli startproject <project_name> [--version <jivas_version>]
    """
    template_path = os.path.join(TEMPLATES_DIR, version, "project")

    if not os.path.exists(template_path):
        click.secho(f"Template for Jivas version {version} not found.", fg="red")
        return

    project_structure: dict = {
        "tests": [],
        "actions": [],
        "daf": [],
        "sh": [],
    }

    try:
        print(f"Creating project: {project_name} (Version: {version})")
        os.makedirs(project_name, exist_ok=True)

        # Create directories
        for folder in project_structure.keys():
            os.makedirs(os.path.join(project_name, folder), exist_ok=True)

        # Copy template files and folders from the selected version
        for root, dirs, files in os.walk(template_path):
            relative_path = os.path.relpath(root, template_path)
            target_dir = os.path.join(project_name, relative_path)

            # Create directories
            for dir_name in dirs:
                os.makedirs(os.path.join(target_dir, dir_name), exist_ok=True)

            # Copy files
            for file_name in files:
                template_file_path = os.path.join(root, file_name)
                target_file_path = os.path.join(target_dir, file_name)

                with open(template_file_path, "r") as template_file:
                    contents = template_file.read()

                # Write `.env` instead of `env.example`
                if file_name == "env.example":
                    target_file_path = os.path.join(target_dir, ".env")

                with open(target_file_path, "w") as project_file:
                    project_file.write(contents)

        click.secho(
            f"Successfully created Jivas project: {project_name} (Version: {version})",
            fg="green",
        )

    except Exception as e:
        click.secho(f"Error creating project: {e}", fg="red")
