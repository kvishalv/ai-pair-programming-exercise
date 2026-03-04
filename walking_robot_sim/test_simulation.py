import pytest

from walking_robot_sim import simulate_robot


def test_no_commands_results_in_zero_distance():
    assert simulate_robot([]) == 0


def test_simple_forward_movement_updates_distance():
    # Move 3 steps north from origin -> position (0, 3) => distance^2 = 9
    assert simulate_robot([3]) == 9


def test_turning_right_and_moving_east():
    # 2 steps north, turn right, then 2 steps east
    # Path: (0, 0) -> (0, 1) -> (0, 2) -> (1, 2) -> (2, 2)
    # Distances^2: 1, 4, 5, 8 -> max = 8
    commands = [2, -1, 2]
    assert simulate_robot(commands) == 8


def test_turning_left_and_moving_west():
    # 1 step north, left turn (to west), then 2 steps west
    # Path: (0, 0) -> (0, 1) -> (-1, 1) -> (-2, 1)
    # Distances^2: 1, 2, 5 -> max = 5
    commands = [1, -2, 2]
    assert simulate_robot(commands) == 5


def test_obstacle_blocks_movement_but_allows_later_commands():
    # Obstacle directly in front after first step
    # Commands: move 2 north; with obstacle at (0, 2) we should stop at (0, 1)
    # Then turn right and move 3 east.
    # Path: (0, 0) -> (0, 1) [blocked at (0, 2)] -> (1, 1) -> (2, 1) -> (3, 1)
    # Distances^2 along path: 1, 2, 5, 10 -> max = 10
    commands = [2, -1, 3]
    obstacles = {(0, 2)}
    assert simulate_robot(commands, obstacles) == 10


def test_multiple_obstacles_and_turns():
    # Example with several obstacles scattered around
    commands = [4, -1, 3, -2, 2, -1, 4]
    obstacles = {(0, 2), (1, 4), (2, 3), (-1, 1)}
    # Hand-checked final max distance^2 for this configuration
    # Path ends at (7, 3) with max distance^2 = 58
    assert simulate_robot(commands, obstacles) == 58


def test_ignores_unknown_negative_commands():
    # -99 should be ignored; only valid commands affect state
    commands = [3, -99, -1, 2]
    # Path as if -99 were not present:
    # (0,0)->(0,1)->(0,2)->(0,3)-> turn right -> (1,3)->(2,3)
    # Distances^2: 1,4,9,10,13 -> max = 13
    assert simulate_robot(commands) == 13

