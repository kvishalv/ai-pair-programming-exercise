import pytest

from mars_rover import MarsRoverController


def run_sequence(controller, commands):
    """
    Helper to run a sequence of textual commands against the controller.

    Returns the list of results for each command in order.
    """
    results = []
    for cmd in commands:
        results.append(controller.execute(cmd))
    return results


def test_single_rover_basic_movement_and_turns():
    controller = MarsRoverController()

    # Set up a single rover and select it
    results = run_sequence(
        controller,
        [
            "CREATE a",
            "SELECT a",
            "M",
            "M",
            "R",
            "M",
        ],
    )

    last = results[-1]
    assert last.status == "OK"
    assert last.selected_id == "a"
    # Start at (0, 0, N):
    # M -> (0, 1, N)
    # M -> (0, 2, N)
    # R -> (0, 2, E)
    # M -> (1, 2, E)
    assert last.position == (1, 2)
    assert last.direction == "E"


def test_invalid_move_without_selected_rover_reports_error():
    controller = MarsRoverController()

    result = controller.execute("M")

    assert result.status == "ERROR"
    assert "no rover selected" in (result.message or "").lower()
    assert result.selected_id is None
    assert result.position is None
    assert result.direction is None


def test_create_and_select_multiple_rovers_tracks_state_independently():
    controller = MarsRoverController()

    results = run_sequence(
        controller,
        [
            "CREATE a",
            "CREATE b",
            "SELECT a",
            "M",  # a -> (0, 1, N)
            "SELECT b",
            "R",  # b: (0, 0, E)
            "M",  # b -> (1, 0, E)
            "SELECT a",
            "M",  # a -> (0, 2, N)
        ],
    )

    last = results[-1]
    assert last.status == "OK"
    assert last.selected_id == "a"
    assert last.position == (0, 2)
    assert last.direction == "N"


def test_delete_rover_and_selection_cleared():
    controller = MarsRoverController()

    results = run_sequence(
        controller,
        [
            "CREATE a",
            "SELECT a",
            "M",
            "DELETE a",
        ],
    )

    last = results[-1]
    assert last.status == "OK"
    assert last.selected_id is None
    assert last.position is None
    assert last.direction is None

    # Further movement commands should fail because no rover is selected
    result_after_delete = controller.execute("M")
    assert result_after_delete.status == "ERROR"
    assert "no rover selected" in (result_after_delete.message or "").lower()


def test_cannot_create_duplicate_rover_id():
    controller = MarsRoverController()

    first = controller.execute("CREATE a")
    duplicate = controller.execute("CREATE a")

    assert first.status == "OK"
    assert duplicate.status == "ERROR"
    assert "already exists" in (duplicate.message or "").lower()


def test_collision_prevents_movement_into_occupied_cell():
    controller = MarsRoverController()

    # b moves north to (0, 2)
    # a moves north to (0, 1)
    # a then attempts to move into (0, 2) which is occupied by b -> blocked
    results = run_sequence(
        controller,
        [
            "CREATE a",
            "CREATE b",
            "SELECT b",
            "M",
            "M",  # b: (0, 2, N)
            "SELECT a",
            "M",  # a: (0, 1, N)
            "M",  # blocked: target (0, 2) occupied by b
        ],
    )

    last = results[-1]
    assert last.status == "BLOCKED"
    assert last.selected_id == "a"
    # a should remain at its previous position with same direction
    assert last.position == (0, 1)
    assert last.direction == "N"


def test_selecting_or_deleting_nonexistent_rover_reports_error():
    controller = MarsRoverController()

    select_result = controller.execute("SELECT x")
    delete_result = controller.execute("DELETE x")

    assert select_result.status == "ERROR"
    assert "does not exist" in (select_result.message or "").lower()
    assert delete_result.status == "ERROR"
    assert "does not exist" in (delete_result.message or "").lower()

