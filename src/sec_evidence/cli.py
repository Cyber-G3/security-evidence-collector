"""Command-line interface."""

from pathlib import Path

import typer

from sec_evidence import __version__
from sec_evidence.evidence_pack import create_evidence_pack, verify_evidence_pack
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
    output: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Directory where the evidence pack will be created.",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """Collect GitHub evidence and create an integrity-verifiable evidence pack."""
    try:
        output.mkdir(parents=True, exist_ok=True)
        with GitHubClient() as client:
            results = collect_repository_metadata(repository, client)
        pack = create_evidence_pack(repository, results, output)
    except ValueError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except AuthenticationError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=3) from exc
    except ApiError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=4) from exc
    except OSError as exc:
        typer.echo(f"ERROR: Could not write evidence pack: {exc}", err=True)
        raise typer.Exit(code=4) from exc

    typer.echo(f"GitHub repository: {repository}")
    for result in results:
        typer.echo(f"{result.status.value:<15} {result.title}: {result.reason}")
    typer.echo(f"Evidence pack: {pack}")


@app.command()
def verify(path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True)) -> None:
    """Verify an evidence pack against its SHA-256 manifest."""
    valid, messages = verify_evidence_pack(path)
    for message in messages:
        typer.echo(message)
    if not valid:
        typer.echo("Evidence integrity verification FAILED.", err=True)
        raise typer.Exit(code=5)
    typer.echo("Evidence integrity verification PASSED.")


@app.command()
def report(path: str) -> None:
    """Generate a report from an evidence pack (planned)."""
    typer.echo(f"Report generation for {path} is not implemented yet.", err=True)
    raise typer.Exit(code=4)


if __name__ == "__main__":
    app()
