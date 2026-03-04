from __future__ import annotations

import sys
from typing import Iterable

from .controller import MarsRoverController


def format_result(result) -> str:
    """
    Convert a CommandResult into a simple, testable line of text.

    Format:
        STATUS selected_id x y direction [ - message ]

    When there is no selected rover, x/y/direction are rendered as "-".
    """
    selected = result.selected_id or "-"
    if result.position is None or result.direction is None:
        x_str = y_str = dir_str = "-"
    else:
        x, y = result.position
        x_str = str(x)
        y_str = str(y)
        dir_str = result.direction

    base = f"{result.status} {selected} {x_str} {y_str} {dir_str}"
    if result.message:
        return f"{base} - {result.message}"
    return base


def run(commands: Iterable[str], *, output_stream) -> None:
    """
    Run a sequence of commands, writing one line of output per command.
    """
    controller = MarsRoverController()
    for raw in commands:
        raw = raw.rstrip("\n")
        if not raw:
            continue
        result = controller.execute(raw)
        print(format_result(result), file=output_stream)


def main(argv: list[str] | None = None) -> int:
    """
    Simple CLI entry point.

    Usage (interactive):
        python -m mars_rover.cli
        CREATE a
        SELECT a
        M
        R
        M

    Or by piping a file of commands:
        python -m mars_rover.cli < commands.txt
    """
    _ = argv  # currently unused, but kept for future extension
    run(sys.stdin, output_stream=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

