"""Runs the jac clean command"""

import subprocess

import click


@click.command(
    help="Clean the Jac files in the current directory and subdirectories. This command executes 'jac clean', which removes compiled Jac artifacts and temporary files. "
    "Use this command to ensure a clean state before rebuilding your Jac project."
)
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean the Jac files in directory."""
    try:
        click.echo("Running jac clean in actions directory...")
        result = subprocess.run(["jac", "clean"], check=True)
        if result.returncode == 0:
            click.echo("Successfully cleaned directory.")

        else:
            click.secho("Failed to clean directory.", fg="red")
            ctx.exit(1)
    except subprocess.CalledProcessError as e:
        click.secho(f"Error running jac clean: {e}", fg="red")
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red")
        ctx.exit(1)
