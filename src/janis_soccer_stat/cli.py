"""Command line entry points."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .db import session_scope
from .scope import ScopeError, apply_scope, describe_scope, load_declaration
from .seeding import seed_countries


def _seed_countries(args: argparse.Namespace) -> int:
    with session_scope() as session:
        count = seed_countries(session)
    print(f"Countries: {count}.")
    return 0


def _scope_apply(args: argparse.Namespace) -> int:
    declaration = load_declaration(args.file)
    with session_scope() as session:
        report = apply_scope(session, declaration)
    print(f"Competitions: {report.competitions}.")
    print(f"Seasons:      {report.seasons}.")
    print(f"Sources:      {report.sources}.")
    for refusal in report.refused:
        print(
            f"Refused {refusal.competition} {refusal.label}: its window of play "
            f"collides with {refusal.collides_with}.",
            file=sys.stderr,
        )
    return 0


def _scope_show(args: argparse.Namespace) -> int:
    with session_scope() as session:
        print(describe_scope(session))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="janis-soccer-stat",
        description="An independent football database for the five major European leagues.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    seed = commands.add_parser(
        "seed-countries", help="register the countries competitions are classified by"
    )
    seed.set_defaults(run=_seed_countries)

    apply_ = commands.add_parser(
        "scope-apply", help="register the declared competitions, seasons and sources (UC-015)"
    )
    apply_.add_argument(
        "--file",
        type=Path,
        default=None,
        help="the scope declaration to apply (default: collection_scope.toml)",
    )
    apply_.set_defaults(run=_scope_apply)

    show = commands.add_parser("scope-show", help="show what is currently declared in scope")
    show.set_defaults(run=_scope_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except ScopeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
