from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set, Tuple


class Direction(str, Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"

    def turn_left(self) -> "Direction":
        order = [Direction.N, Direction.W, Direction.S, Direction.E]
        idx = order.index(self)
        return order[(idx + 1) % len(order)]

    def turn_right(self) -> "Direction":
        order = [Direction.N, Direction.E, Direction.S, Direction.W]
        idx = order.index(self)
        return order[(idx + 1) % len(order)]

    def movement_delta(self) -> Tuple[int, int]:
        if self is Direction.N:
            return 0, 1
        if self is Direction.E:
            return 1, 0
        if self is Direction.S:
            return 0, -1
        if self is Direction.W:
            return -1, 0
        raise ValueError(f"Unsupported direction {self}")


@dataclass
class Rover:
    rover_id: str
    x: int = 0
    y: int = 0
    direction: Direction = Direction.N

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y


@dataclass
class CommandResult:
    status: str
    message: Optional[str]
    selected_id: Optional[str]
    position: Optional[Tuple[int, int]]
    direction: Optional[str]


class MarsRoverController:
    """
    Stateful controller for managing one or more Mars rovers on an unbounded 2D grid.

    Public API:
        execute(command: str) -> CommandResult

    Supported commands:
        - CREATE <id>
        - DELETE <id>
        - SELECT <id>
        - L (turn left 90° for selected rover)
        - R (turn right 90° for selected rover)
        - M (move selected rover forward by 1 cell, with collision prevention)

    The controller maintains:
        - A mapping of rover IDs to rover state.
        - The ID of the currently selected rover (or None).
        - An index of occupied grid cells to prevent collisions.
    """

    def __init__(self) -> None:
        self._rovers: Dict[str, Rover] = {}
        self._selected_id: Optional[str] = None
        # Map from position (x, y) to set of rover IDs occupying that cell.
        self._position_index: Dict[Tuple[int, int], Set[str]] = {}

    # Public API ---------------------------------------------------------

    def execute(self, raw_command: str) -> CommandResult:
        """
        Parse and execute a single textual command.

        After every command, a CommandResult is returned that includes:
            - status: "OK", "ERROR", or "BLOCKED"
            - message: optional human-readable detail
            - selected_id: ID of the currently selected rover (or None)
            - position: (x, y) of the selected rover, if any
            - direction: "N", "E", "S", "W" for the selected rover, if any
        """
        command = raw_command.strip()
        if not command:
            return self._error("empty command")

        parts = command.split()
        op = parts[0].upper()

        if op == "CREATE":
            if len(parts) != 2:
                return self._error("CREATE requires a rover id")
            rover_id = parts[1]
            return self._create(rover_id)

        if op == "DELETE":
            if len(parts) != 2:
                return self._error("DELETE requires a rover id")
            rover_id = parts[1]
            return self._delete(rover_id)

        if op == "SELECT":
            if len(parts) != 2:
                return self._error("SELECT requires a rover id")
            rover_id = parts[1]
            return self._select(rover_id)

        if op in {"L", "R", "M"} and len(parts) == 1:
            return self._movement_or_turn(op)

        return self._error(f"unknown or invalid command syntax: {raw_command}")

    # Internal helpers ---------------------------------------------------

    def _create(self, rover_id: str) -> CommandResult:
        if rover_id in self._rovers:
            return self._error(f"rover '{rover_id}' already exists")

        rover = Rover(rover_id=rover_id)
        self._rovers[rover_id] = rover
        # Mark the starting position as occupied by this rover
        self._occupy(rover.position, rover.rover_id)
        return self._ok(f"created rover '{rover_id}'")

    def _delete(self, rover_id: str) -> CommandResult:
        rover = self._rovers.get(rover_id)
        if rover is None:
            return self._error(f"rover '{rover_id}' does not exist")

        # Free its cell
        self._vacate(rover.position, rover.rover_id)
        del self._rovers[rover_id]

        if self._selected_id == rover_id:
            self._selected_id = None
            return CommandResult(
                status="OK",
                message=f"deleted rover '{rover_id}', no rover selected",
                selected_id=None,
                position=None,
                direction=None,
            )

        return self._ok(f"deleted rover '{rover_id}'")

    def _select(self, rover_id: str) -> CommandResult:
        if rover_id not in self._rovers:
            return self._error(f"rover '{rover_id}' does not exist")

        self._selected_id = rover_id
        return self._snapshot(status="OK", message=f"selected rover '{rover_id}'")

    def _movement_or_turn(self, op: str) -> CommandResult:
        rover = self._current_rover()
        if rover is None:
            return self._error("no rover selected; cannot apply movement or turn command")

        if op == "L":
            rover.direction = rover.direction.turn_left()
            return self._snapshot(status="OK", message="turned left")

        if op == "R":
            rover.direction = rover.direction.turn_right()
            return self._snapshot(status="OK", message="turned right")

        if op == "M":
            dx, dy = rover.direction.movement_delta()
            target = (rover.x + dx, rover.y + dy)

            # If the target cell is occupied by another rover, block the move.
            occupants = self._position_index.get(target)
            if occupants and (occupants - {rover.rover_id}):
                return self._snapshot(
                    status="BLOCKED",
                    message="move blocked: target cell already occupied",
                )

            # Move: free old cell, occupy new cell.
            self._vacate(rover.position, rover.rover_id)
            rover.x, rover.y = target
            self._occupy(rover.position, rover.rover_id)
            return self._snapshot(status="OK", message="moved forward")

        return self._error(f"unsupported operation {op}")

    def _current_rover(self) -> Optional[Rover]:
        if self._selected_id is None:
            return None
        return self._rovers.get(self._selected_id)

    def _snapshot(self, status: str, message: Optional[str]) -> CommandResult:
        rover = self._current_rover()
        if rover is None:
            return CommandResult(
                status=status,
                message=message,
                selected_id=None,
                position=None,
                direction=None,
            )

        return CommandResult(
            status=status,
            message=message,
            selected_id=self._selected_id,
            position=rover.position,
            direction=rover.direction.value,
        )

    def _ok(self, message: Optional[str] = None) -> CommandResult:
        return self._snapshot(status="OK", message=message)

    def _error(self, message: str) -> CommandResult:
        rover = self._current_rover()
        if rover is None:
            return CommandResult(
                status="ERROR",
                message=message,
                selected_id=None,
                position=None,
                direction=None,
            )

        return CommandResult(
            status="ERROR",
            message=message,
            selected_id=self._selected_id,
            position=rover.position,
            direction=rover.direction.value,
        )

    # Position index helpers ---------------------------------------------

    def _occupy(self, position: Tuple[int, int], rover_id: str) -> None:
        """Mark a grid cell as occupied by the given rover."""
        occupants = self._position_index.setdefault(position, set())
        occupants.add(rover_id)

    def _vacate(self, position: Tuple[int, int], rover_id: str) -> None:
        """Remove the given rover from the specified grid cell."""
        occupants = self._position_index.get(position)
        if not occupants:
            return
        occupants.discard(rover_id)
        if not occupants:
            # Remove empty entry to keep the index compact.
            del self._position_index[position]

