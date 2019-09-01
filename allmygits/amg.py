# -*- coding: utf-8 -*-
import pathlib
import re
import subprocess

import click
from typing import Iterable, List


@click.group("amg")
def cli():
    pass


@cli.command("status")
@click.argument(
    "paths", type=click.Path(file_okay=False, exists=True), nargs=-1, required=True
)
@click.option("--fetch/--no-fetch", default=True)
def status(paths, fetch):
    git_dirs = get_git_directories(paths)

    for d in git_dirs:
        if fetch:
            subprocess.run(["git", "fetch", "--quiet"], cwd=str(d))

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
            r_status = click.style("+", fg="red") + " "

        # Repository parent directory, for multiple inputs.
        r_parent = str(d.parent).replace(str(pathlib.Path.home()), "~")

        # Output
        click.echo(f"{r_status}{r_name} ({r_branch}) [{r_parent}]")


def get_git_directories(paths: Iterable[str]) -> List[pathlib.Path]:
    """Return a list of git directories in the given paths."""
    git_dirs = []
    for path in paths:
        for d in pathlib.Path(path).iterdir():
            if (d / ".git").exists():
                git_dirs.append(d)
    return git_dirs


if __name__ == "__main__":
    cli()
