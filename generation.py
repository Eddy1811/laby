from random import randint
import random
import time
from maze_constants import WALL, VISITED, START, GOAL, EMPTY


def printStep(maze, maze_effect, randomColor=False, shortestPath=[], refresh=False):
    """Update the maze and refresh the screen."""
    maze_effect.update_maze(maze, randomColor=randomColor, shortestPath=shortestPath)
    if refresh:
        maze_effect.maze_widget.update(0)


# Helper functions
def checkBounds(maze, x, y):
    return 0 <= x < len(maze) and 0 <= y < len(maze[0])


def getNeighbors2(x, y):
    return [[x, y - 2], [x + 2, y], [x, y + 2], [x - 2, y]]


def checkNotVisited(lab, x, y):
    return lab[x][y] == WALL if checkBounds(lab, x, y) else False


def generateLabyrinth(width, height):
    maze = [
        [
            WALL if (i % 2 == 1 or j % 2 == 1) else i * height // 2 + j // 2
            for j in range(height)
        ]
        for i in range(width)
    ]
    return maze


def mergeMazeGeneration(maze, width, height, maze_effect, chance=0.1):
    done = False

    first_step = True

    while not done:
        # Pick a random valid cell
        while True:
            if first_step:
                posX, posY = (
                    randint(0, width // 2 - 1) * 2,
                    randint(0, height // 2 - 1) * 2,
                )
                first_step = False
            else:
                posX, posY = (
                    randint(0, width - 1),
                    randint(0, height - 1),
                )
                while maze[posX][posY] == WALL:
                    posX, posY = (
                        randint(0, width - 1),
                        randint(0, height - 1),
                    )

            value = maze[posX][posY]
            neighbors = getNeighbors2(posX, posY)

            # Filter valid neighboring cells
            possibleCases = [
                n
                for n in neighbors
                if checkBounds(maze, n[0], n[1])
                and (maze[n[0]][n[1]] != value or random.random() <= chance)
                and maze[n[0]][n[1]] != WALL
            ]
            if possibleCases:
                break

        # Choose a random neighboring cell
        nextCase = possibleCases[randint(0, len(possibleCases) - 1)]
        nextX, nextY = nextCase
        wallX, wallY = (posX + nextX) // 2, (posY + nextY) // 2

        # Merge cells and update the maze
        newValue = min(maze[posX][posY], maze[nextX][nextY])
        oldValue = max(maze[posX][posY], maze[nextX][nextY])

        for i in range(width):
            for j in range(height):
                if maze[i][j] == oldValue:
                    maze[i][j] = newValue

        # Update the wall between the two cells
        maze[wallX][wallY] = newValue

        # Update the maze and render the step (with random color effect)
        printStep(maze, maze_effect, randomColor=True)

        # Check if all cells are merged (i.e., no different values)
        done = all(
            maze[i][j] in (WALL, newValue) for i in range(width) for j in range(height)
        )


def clear_maze(lab, clearStartAndGoal=False):
    for row in lab:
        for i in range(len(row)):
            if row[i] != WALL and (clearStartAndGoal or row[i] not in (START, GOAL)):
                row[i] = EMPTY


def append_start_and_goal(maze, width, height):
    start, goal = None, None

    while not start:
        sX, sY = randint(0, width - 1), randint(0, height - 1)
        if maze[sX][sY] != WALL:
            start = [sX, sY]
            maze[sX][sY] = START

    while not goal:
        gX, gY = randint(0, width - 1), randint(0, height - 1)
        if maze[gX][gY] != WALL and [gX, gY] != start:
            goal = [gX, gY]
            maze[gX][gY] = GOAL

    return [start, goal]
