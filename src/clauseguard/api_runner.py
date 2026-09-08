"""
api_runner.py — thin wrapper so `clauseguard-api` starts the FastAPI server.

Usage:
    clauseguard-api                    # default: localhost:8000
    clauseguard-api --host 0.0.0.0 --port 8080
"""
import typer
import uvicorn

runner = typer.Typer(help="Start the ClauseGuard FastAPI server.")


@runner.command()
def main(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(8000,        help="Bind port"),
    reload: bool = typer.Option(False,    help="Auto-reload on code changes (dev mode)"),
):
    uvicorn.run("clauseguard.api:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    runner()
