"""Command-line interface."""

import typer

from sec_evidence import __version__
from sec_evidence.exceptions import ApiError, AuthenticationError
from sec_evidence.github_client import GitHubClient
from sec_evidence.github_collector import collect_repository_metadata

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
    """Collect deterministic GitHub repository metadata."""
    try:
        with GitHubClient() as client:
            results = collect_repository_metadata(repository, client)
    except ValueError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except AuthenticationError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=3) from exc
    except ApiError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=4) from exc

    typer.echo(f"GitHub repository: {repository}")
    for result in results:
        typer.echo(f"{result.status.value:<15} {result.title}: {result.reason}")


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
