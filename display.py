from asciimatics.screen import Screen
import re
from time import sleep

# Labyrinth Symbols
EMPTY = "▮"
WALL = "🟫"
VISITED = "🐾"
BADWAY = "🍫"
GOAL = "🦴"
START = "🐶"

# Define the colors (asciimatics uses integers for colors)
COLOR_MAP = {
    "🟫": Screen.COLOUR_WHITE,  # WALL
    "▮": Screen.COLOUR_BLACK,  # EMPTY
    "🐾": Screen.COLOUR_CYAN,  # VISITED
    "🍫": Screen.COLOUR_YELLOW,  # BADWAY
    "🦴": Screen.COLOUR_GREEN,  # GOAL
    "🦑": Screen.COLOUR_RED,  # START
}


# Helper functions
def checkBounds(maze, x, y):
    sizeX = len(maze)
    sizeY = len(maze[0])
    return x < sizeX and y < sizeY and x >= 0 and y >= 0


def getNorth(x, y):
    return [x, y - 1]


def getSouth(x, y):
    return [x, y + 1]


def getEast(x, y):
    return [x + 1, y]


def getWest(x, y):
    return [x - 1, y]


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


def printLabyrinth(screen, laby, randomColor=False, shortestPath=[], BFS=False):
    # Get original dimensions of the maze
    sizeX = len(laby)
    sizeY = len(laby[0])

    # Add walls around the maze
    # Add walls to the left and right of each row
    laby_with_walls = [[WALL] + row + [WALL] for row in laby]
    # Add top and bottom wall rows
    top_bottom_wall_row = [WALL] * (sizeX + 2)
    laby_with_walls = [top_bottom_wall_row] + laby_with_walls + [top_bottom_wall_row]

    # Update sizeX and sizeY to the new dimensions
    sizeX = len(laby_with_walls)
    sizeY = len(laby_with_walls[0])

    # Calculate the fixed width of each cell (equals to the number of characters in the biggest cell)
    fixedWidth = getFixedWidth(sizeX, sizeY)

    # Loop through each row
    for i in range(sizeY):
        for j in range(sizeX):
            cell = laby_with_walls[j][i]
            color = COLOR_MAP.get(cell, Screen.COLOUR_WHITE)

            # Handle cases where the cell contains a number or letter
            if re.match("^[0-9]*$", str(cell)) or re.match("^[A-Z]*$", str(cell)):
                # Add a random color, but same color for the same number
                if randomColor:
                    color = hash(str(cell)) % 255 + 16

                # If BFS is running, color the visited cells, from yellow to red, the farther the redder
                if BFS and (cell == VISITED or str(cell).isdigit()):
                    if str(cell).isdigit():
                        if int(cell) > 100 * fixedWidth:
                            color = Screen.COLOUR_CYAN
                        elif int(cell) > 60 * fixedWidth:
                            color = Screen.COLOUR_BLUE
                        elif int(cell) > 30 * fixedWidth:
                            color = Screen.COLOUR_RED
                        elif int(cell) > 10 * fixedWidth:
                            color = Screen.COLOUR_MAGENTA
                        elif int(cell) > 0:
                            color = Screen.COLOUR_YELLOW

                if [j, i] in shortestPath:
                    color = Screen.COLOUR_GREEN
                    cell = VISITED
                # Remove spaces from the start and goal only to test
                cellWithoutSpaces = str(cell).replace(" ", "")
                if cellWithoutSpaces == "0":
                    cell = START

                screen.print_at(
                    f"{cell}".center(fixedWidth),
                    j * fixedWidth,
                    i,
                    colour=color,
                )
            else:
                # Get the corresponding character and color
                screen.print_at(
                    cell.center(fixedWidth), j * fixedWidth, i, colour=color
                )

    screen.refresh()


def displayShortestPath(screen, maze, goal, path):
    curPos = goal
    x, y = curPos[0], curPos[1]
    shortestPath = []
    while str(maze[x][y]) != "0":
        shortestPath.append([x + 1, y + 1])

        possibleMoves = []
        if checkCaseIsDigit(maze, getNorth(x, y)):
            possibleMoves.append(getNorth(x, y))
        if checkCaseIsDigit(maze, getEast(x, y)):
            possibleMoves.append(getEast(x, y))
        if checkCaseIsDigit(maze, getSouth(x, y)):
            possibleMoves.append(getSouth(x, y))
        if checkCaseIsDigit(maze, getWest(x, y)):
            possibleMoves.append(getWest(x, y))

        nextCase = None
        min_val = 10000000
        for move in possibleMoves:
            moveValue = int(maze[move[0]][move[1]])
            if moveValue < min_val:
                nextCase = move
                min_val = moveValue

        if nextCase is None:
            screen.print_at("No path found", 0, len(maze[0]) + 1)
            screen.refresh()
            return

        x, y = nextCase[0], nextCase[1]

        printStep(screen, maze, shortestPath=shortestPath, BFS=True)

    # Color the start
    # shortestPath.append([x + 1, y + 1])
    printStep(screen, maze, shortestPath=shortestPath, BFS=True)
    # sleep(1)

    # # Remove all number except the shortest path
    #    for i in range(len(maze)):
    #        for j in range(len(maze[i])):
    #            if maze[i][j] != WALL and [i, j] not in shortestPath:
    #                maze[i][j] = EMPTY
    #
    # printStep(screen, maze, shortestPath=shortestPath, BFS=True)


def colorAt(screen, maze, pos, color):
    x, y = pos[0], pos[1]
    fixedWidth = getFixedWidth(len(maze), len(maze[0]))
    cell_value = str(maze[x][y]).center(fixedWidth)
    screen.print_at(cell_value, x * fixedWidth, y, colour=color)


def getValueWithoutColor(value):
    # Remove color codes if present
    return re.sub(r"\033\[[0-9;]*m", "", value)


def checkCaseIsDigit(maze, pos):
    x, y = pos[0], pos[1]
    if not checkBounds(maze, x, y):
        return False
    return (str(maze[x][y]).isdigit() or maze[x][y] == VISITED) and str(
        maze[x][y]
    ) != WALL


def printStep(screen, maze, randomColor=False, shortestPath=[], BFS=False):
    if screen.has_resized():
        screen.clear()
        screen.refresh()
    # screen.clear()
    # sleep(0.1)
    printLabyrinth(screen, maze, randomColor, shortestPath, BFS)
    screen.refresh()
