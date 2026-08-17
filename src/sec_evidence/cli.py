"""Command-line interface."""

import typer

from sec_evidence import __version__

app = typer.Typer(help="Collect, normalize, verify and map security evidence.")
collect_app = typer.Typer(help="Collect evidence from supported providers.")
app.add_typer(collect_app, name="collect")


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(f"Security Evidence Collector {__version__}")


@collect_app.command("github")
def collect_github(
    repository: str = typer.Argument(..., help="Repository in OWNER/REPO form."),
) -> None:
    """GitHub collector placeholder for the next implementation phase."""
    typer.echo(
        f"GitHub collector for {repository} is not implemented in v0.1-dev yet.",
        err=True,
    )
    raise typer.Exit(code=4)


@app.command()
def verify(path: str) -> None:
    """Verify an evidence pack (planned)."""
    typer.echo(f"Evidence-pack verification for {path} is not implemented yet.", err=True)
    raise typer.Exit(code=4)


@app.command()
def report(path: str) -> None:
    """Generate a report from an evidence pack (planned)."""
    typer.echo(f"Report generation for {path} is not implemented yet.", err=True)
    raise typer.Exit(code=4)


if __name__ == "__main__":
    app()
