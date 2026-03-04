from collections.abc import Iterable
from typing import Iterable as TypingIterable, Tuple, Set


def simulate_robot(
    commands: Iterable[int],
    obstacles: Iterable[Tuple[int, int]] | None = None,
) -> int:
    """
    Simulate a walking robot on an infinite grid.

    The robot:
    - Starts at (0, 0) facing "north" (positive y-axis).
    - Accepts commands:
        - -2: turn left 90 degrees.
        - -1: turn right 90 degrees.
        - n > 0: attempt to move forward n unit steps, stopping early if
          the next cell would be an obstacle.
    - Uses fast obstacle lookup (hash set) while stepping.
    - Tracks and returns the maximum squared Euclidean distance from the
      origin reached at any point during the walk.

    Args:
        commands: Sequence of integers representing commands.
        obstacles: Iterable of (x, y) coordinates that are blocked.

    Returns:
        Maximum squared Euclidean distance from the origin reached.
    """
    # Direction order: North, East, South, West.
    directions: list[tuple[int, int]] = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    dir_idx = 0  # Start facing north.

    x, y = 0, 0
    max_dist_sq = 0

    obstacle_set: Set[Tuple[int, int]] = set(obstacles or [])

    for cmd in commands:
        if cmd == -2:  # Turn left.
            dir_idx = (dir_idx - 1) % 4
        elif cmd == -1:  # Turn right.
            dir_idx = (dir_idx + 1) % 4
        elif cmd > 0:
            dx, dy = directions[dir_idx]
            for _ in range(cmd):
                next_x = x + dx
                next_y = y + dy
                if (next_x, next_y) in obstacle_set:
                    # Stop this move when we would hit an obstacle.
                    break
                x, y = next_x, next_y
                max_dist_sq = max(max_dist_sq, x * x + y * y)
        else:
            # Ignore any other non-specified commands.
            continue

    return max_dist_sq


def _example() -> None:
    """
    Simple example for manual testing.
    """
    commands = [4, -1, 3, -2, 2]
    obstacles = {(2, 4)}
    result = simulate_robot(commands, obstacles)
    print(f"Max distance^2: {result}")


if __name__ == "__main__":
    _example()

