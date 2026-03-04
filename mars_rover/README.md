Mars Rover Controller
======================

This package implements a small, testable **multi‑rover Mars controller** on an unbounded 2D grid.

Each rover:

- Starts at `(0, 0)` facing **North**.
- Can turn left/right in 90° increments.
- Can move forward one cell at a time.
- Is uniquely identified by a string ID.

Multiple rovers can exist simultaneously, and a simple collision‑avoidance rule prevents a rover from moving into a cell that is already occupied by another rover.


Command model
-------------

The core API is exposed via `MarsRoverController.execute(command: str) -> CommandResult`.

Supported commands:

- `CREATE <id>` – create a new rover at `(0, 0, N)`.
- `DELETE <id>` – delete an existing rover.
- `SELECT <id>` – make a rover the **active** rover.
- `L` – turn the active rover left 90°.
- `R` – turn the active rover right 90°.
- `M` – move the active rover forward one cell in its current direction.

Behavior rules:

- Movement/turn commands (`L`, `R`, `M`) require a selected rover; otherwise an error is returned.
- Rover IDs must be unique (`CREATE` with an existing ID is an error).
- If `M` would move a rover into a cell occupied by another rover, the move is **blocked** and the rover stays in place.

`CommandResult` includes:

- `status`: `"OK"`, `"ERROR"`, or `"BLOCKED"`.
- `message`: optional human‑readable detail.
- `selected_id`: ID of the currently selected rover (or `None`).
- `position`: `(x, y)` of the selected rover, if any.
- `direction`: `"N"`, `"E"`, `"S"`, or `"W"` of the selected rover, if any.


CLI usage
---------

There is a small CLI in `cli.py` that reads commands from stdin and prints one line of output per command.

From the project root:

```bash
python -m mars_rover.cli
```

Example interactive session:

```text
CREATE a
SELECT a
M
R
M
```

You can also pipe a file of commands:

```bash
python -m mars_rover.cli < commands.txt
```

Output format
-------------

For every non‑empty input line, the CLI prints:

```text
STATUS selected_id x y direction - message
```

Where:

- `STATUS` is `OK`, `ERROR`, or `BLOCKED`.
- `selected_id` is the active rover ID, or `-` if none.
- `x y direction` describe the active rover’s state, or `- - -` if none is selected.
- `message` is omitted if empty; otherwise it explains what happened (e.g., move blocked, invalid command, rover created).


Running tests
-------------

Tests are written with `pytest` and live in `mars_rover/test_controller.py`.

From the project root, run:

```bash
pytest
```

This executes both the Mars rover tests and the other exercises in the repository.

