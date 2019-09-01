# All My Gits

Check the status of all git repositories in one or more parent directories. 

## Usage

The following example illustrates basic usage that has been implemented so far:

    $ amg status ~/projects
    toggl-watcher (master) [~/projects]
    aws-lambda-perl (master) [~/projects]
    spruce (master) [~/projects]
    + lambdalatex (v2-api) [~/projects]
    + allmygits (master) [~/projects]
    aws-lambda-texlive (master) [~/projects]
    MultiMarkdown-6 (fix-mmd6-includes) [~/projects]

From left to right on each line, we have the repository name, the current branch in parentheses, and its parent directory in square brackets.
The `+` sign indicates that the local repository has untracked or modified files compared to the same origin branch.
In the future, this indicator will provide more information about the nature of the differences.
