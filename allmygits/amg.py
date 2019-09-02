# -*- coding: utf-8 -*-
import asyncio
import pathlib
import re
import subprocess
from typing import Iterable, Tuple

import click


def validate_paths(ctx, param, value: Iterable[str]) -> Tuple[pathlib.Path]:
    """Return a list of git directories in the given paths."""
    git_dirs = []
    for path in value:
        for d in pathlib.Path(path).iterdir():
            if (d / ".git").exists():
                git_dirs.append(d)
    if git_dirs:
        return tuple(git_dirs)
    raise click.BadParameter("No git repositories were located.", ctx=ctx, param=param)


@click.group("amg")
def cli():
    pass


@cli.command("status")
@click.argument(
    "paths",
    type=click.Path(file_okay=False, exists=True),
    nargs=-1,
    required=True,
    callback=validate_paths,
)
@click.option("--fetch/--no-fetch", default=True)
def status(paths, fetch):
    if fetch:
        git_fetch(paths)

    for d in paths:
        r = subprocess.run(
            ["git", "status", "--branch", "--porcelain"],
            cwd=str(d),
            text=True,
            capture_output=True,
        )

        # Start building up the output line.
        r_name = d.stem

        # Get the name of the branch, if one exists.
        # Call out None (case without remote repo) and non-master branches.
        m = re.match(r"## (.+)\.\.\.", r.stdout)
        r_branch = m.group(1) if m else click.style("None", fg="red")
        if r_branch not in ("master", "None"):
            r_branch = click.style(r_branch, fg="blue")

        # Simply check for untracked changes/files for now.
        # Repos without branches assumed to be not pushed to remote.
        r_status = ""
        if "??" in r.stdout or "None" in r_branch:
            r_status = click.style("+", fg="red")
        if " M " in r.stdout:  # locally modified file
            r_status += click.style("M", fg="red")
        if "[ahead " in r.stdout:  # local ahead of origin
            r_status += click.style("^", fg="red")
        if r_status != "":
            r_status += " "

        # Repository parent directory, for multiple inputs.
        r_parent = str(d.parent).replace(str(pathlib.Path.home()), "~")

        # Output
        click.echo(f"{r_status}{r_name} ({r_branch}) [{r_parent}]")


def git_fetch(paths: Iterable[pathlib.Path]):
    """Perform a git fetch on all directories in the given path."""

    async def run_in_parallel(cmd):
        await (await asyncio.create_subprocess_shell(cmd)).communicate()

    async def fetch_in_parallel():
        await asyncio.gather(*[run_in_parallel(cmd) for cmd in commands])

    commands = [f"cd {d} && git fetch --quiet" for d in paths]
    asyncio.run(fetch_in_parallel())


if __name__ == "__main__":
    cli()
