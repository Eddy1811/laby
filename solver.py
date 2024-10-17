from collections import deque
from asciimatics.screen import Screen
from generation import checkBounds
from maze_constants import EMPTY, VISITED, BADWAY, GOAL, START, WALL


def print_step(maze, maze_effect, shortest_path=[], randomColor=False, refresh=False):
    """Update the maze and refresh the screen."""
    maze_effect.update_maze(maze, randomColor=randomColor, shortestPath=shortest_path)

    if refresh:
        maze_effect.maze_widget.need_update = True
        maze_effect.maze_widget.update(0)


def check_bounds(maze, x, y):
    """Check if a position is within maze bounds."""
    return 0 <= x < len(maze) and 0 <= y < len(maze[0])


def get_neighbors(x, y):
    """Get the four possible neighbors (N, E, S, W)."""
    return [[x, y - 1], [x + 1, y], [x, y + 1], [x - 1, y]]


def check_cell(maze, vec2):
    """Check if the given vector position is traversable or is the goal."""
    x, y = vec2
    return check_bounds(maze, x, y) and (maze[x][y] == EMPTY or maze[x][y] == GOAL)


def visit(maze, pos, step):
    """Mark a cell as visited with the current step."""
    maze[pos[0]][pos[1]] = step


def bad_way(maze, pos):
    """Mark a cell as part of a bad way."""
    maze[pos[0]][pos[1]] = BADWAY


def DFS(maze, maze_effect, start=[0, 0], step=0):
    """Non-recursive Depth-First Search (DFS) implementation."""
    path = [start]
    visit(maze, start, step)
    print_step(maze, maze_effect)

    while path:
        curPos = path[-1]
        x, y = curPos

        # Try to find a valid neighboring cell
        nextCase = None
        for neighbor in get_neighbors(x, y):
            if check_cell(maze, neighbor):
                nextCase = neighbor
                break

        if nextCase:
            if maze[nextCase[0]][nextCase[1]] == GOAL:
                path.append(nextCase)
                print_step(maze, maze_effect)
                return
            # Move to the next valid cell
            path.append(nextCase)
            step += 1
            visit(maze, nextCase, step)
            print_step(maze, maze_effect)
        else:
            # Backtrack
            bad_way(maze, curPos)
            path.pop()
            print_step(maze, maze_effect)

    raise Exception("No solution")


def BFS(maze, maze_effect, start=[0, 0], step=0):
    """Breadth-First Search (BFS) implementation."""
    queue = deque([start])
    visited = set([tuple(start)])  # To avoid revisiting cells

    while queue:
        curPos = queue.popleft()
        x, y = curPos

        # If goal is found, return
        if maze[x][y] == GOAL:
            print_step(maze, maze_effect)
            return

        # Visit current cell
        if maze[x][y] == EMPTY or str(maze[x][y]).isdigit():
            visit(maze, curPos, step)
            print_step(maze, maze_effect)
            step += 1

        # Add all valid neighbors to the queue
        for neighbor in get_neighbors(x, y):
            if check_cell(maze, neighbor) and tuple(neighbor) not in visited:
                visited.add(tuple(neighbor))
                queue.append(neighbor)

    raise Exception("No solution")


def isdigit(maze, x, y):
    if check_bounds(maze, x, y):
        return (
            str(maze[x][y]).isdigit()
            and maze[x][y] != GOAL
            and maze[x][y] != START
            and maze[x][y] != VISITED
            and maze[x][y] != WALL
        )
    return False


def compute_shortest_path(maze, goal, maze_effect):
    x, y = goal
    shortest_path = [goal]

    while maze[x][y] != START and (str(maze[x][y]).isdigit() or maze[x][y] != 0):
        cell = maze[x][y]

        if str(cell).isdigit():
            cell = int(cell)

        # Get the neighbors of the current cell
        # and find the one with the smallest value
        # to move towards the start
        neighbors = get_neighbors(x, y)
        next_cell = None
        min_value = 999999
        for neighbor in neighbors:
            if (
                checkBounds(maze, neighbor[0], neighbor[1])
                and maze[neighbor[0]][neighbor[1]] == START
            ):
                next_cell = neighbor
                shortest_path.append(next_cell)
                print_step(maze, maze_effect, shortest_path=shortest_path)
                return shortest_path
            if isdigit(maze, neighbor[0], neighbor[1]):
                if next_cell is None or maze[neighbor[0]][neighbor[1]] < min_value:
                    next_cell = neighbor

                    min_value = maze[neighbor[0]][neighbor[1]]

        if next_cell:
            x, y = next_cell
            maze[x][y] = VISITED
            shortest_path.append(next_cell)
            print_step(maze, maze_effect, shortest_path=shortest_path)
        else:
            # No next cell found, break the loop
            break

    return shortest_path
