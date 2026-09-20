def main() -> None:
    """Entry point of the janis-soccer-stat command."""
    from .cli import main as run

    raise SystemExit(run())
