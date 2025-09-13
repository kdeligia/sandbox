from collections import deque
from collections.abc import Sequence


def neighbors(current: tuple[int, int], rows: int, cols: int):
    r, c = current
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


def bfs_maze_problem(
    grid: Sequence[Sequence[int]], start: Sequence[int], goal: Sequence[int]
) -> list[tuple[int, int]]:
    """
    Breadth-First Search: returns shortest path as list of (r, c), or [] if none.
    """
    rows, cols = len(grid), len(grid[0])
    start_row, start_column = start
    end_row, end_column = goal
    if start_row > rows or end_row > rows or start_column > cols or end_column > cols:
        raise ValueError("Invalid start or end!")

    q = deque([start])
    visited = {start}
    parent = {start: None}

    while q:
        current_cell = q.popleft()
        if current_cell == goal:
            return _create_path(current_cell, parent)
        for nr, nc in neighbors(current_cell, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] == 1:
                visited.add((nr, nc))
                parent[(nr, nc)] = current_cell
                q.append((nr, nc))
    return []


def dfs_maze_problem(
    grid: Sequence[Sequence[int]], start: tuple[int, int], goal: tuple[int, int]
) -> list[tuple[int, int]]:
    """
    Depth-First Search (iterative): returns *a* path (not guaranteed shortest),
    as list of (r, c), or () if none.
    """
    rows, cols = len(grid), len(grid[0])
    start_row, start_column = start
    end_row, end_column = goal
    if start_row > rows or end_row > rows or start_column > cols or end_column > cols:
        raise ValueError("Invalid start or end!")

    stack = [start]
    visited = {start}
    parent = {start: None}

    while stack:
        current_cell = stack.pop()
        if current_cell == goal:
            return _create_path(current_cell, parent)
        for nr, nc in neighbors(current_cell, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] == 1:
                visited.add((nr, nc))
                parent[(nr, nc)] = current_cell
                stack.append((nr, nc))
    return []


def _create_path(
    current: tuple[int, int],
    parent: dict[tuple[int, int], None | tuple[int, int]],
) -> list[tuple[int, int]]:
    path = []
    while current is not None:
        path.append(current)
        current = parent[current]
    return path[::-1]
