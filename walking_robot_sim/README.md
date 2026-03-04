# Walking Robot Simulation

Simulate a robot on an infinite grid executing turn commands and unit-step moves, stopping any step that would hit an obstacle and updating its facing direction as instructed. Use fast obstacle lookup (e.g., a hash set) while stepping through commands to track and return the maximum squared Euclidean distance from the origin reached.

## Overview

The robot:
- **Starts** at \((0, 0)\) facing north (positive y-axis).
- **Commands**:
  - **-2**: turn left 90 degrees.
  - **-1**: turn right 90 degrees.
  - **n > 0**: attempt to move forward \(n\) unit steps, one cell at a time.
- **Obstacles**:
  - Before each single step, the robot checks whether the next cell is an obstacle.
  - If the next cell is blocked, it **stops that move command** but continues processing subsequent commands.
- **Output**:
  - While executing commands, track the **maximum squared Euclidean distance** from the origin \((0, 0)\), i.e. \(x^2 + y^2\).
  - Return this maximum value at the end of the simulation.

## Python API

The core API is provided by `simulate_robot`:

```python
from walking_robot_sim import simulate_robot

commands = [4, -1, 3, -2, 2]
obstacles = {(2, 4)}
max_dist_sq = simulate_robot(commands, obstacles)
print(max_dist_sq)
```

