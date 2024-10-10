from asciimatics.screen import Screen
import re
from time import sleep

# Labyrinth Symbols
EMPTY = "▮"
WALL = "■"
VISITED = "▫"
BADWAY = "⛝"
GOAL = "⚿"

# Define the colors (asciimatics uses integers for colors)
COLOR_MAP = {
    "▮": Screen.COLOUR_BLACK,  # WALL
    "■": Screen.COLOUR_WHITE,  # EMPTY
    "▫": Screen.COLOUR_CYAN,  # VISITED
    "⛝": Screen.COLOUR_YELLOW,  # BADWAY
    "⚿": Screen.COLOUR_GREEN,  # GOAL
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


# Function to render the labyrinth
def printLabyrinth(screen, laby, randomColor=False, shortestPath=[]):
    sizeX = len(laby)
    sizeY = len(laby[0])

    # Calculate the fixed width of each cell (equals to the number of characters in the biggest cell)
    fixedWidth = getFixedWidth(sizeX, sizeY)

    # Loop through each row
    for i in range(sizeY):
        for j in range(sizeX):
            cell = laby[j][i]
            color = COLOR_MAP.get(cell, Screen.COLOUR_WHITE)

            # Handle cases where the cell contains a number or letter
            if re.match("^[0-9]*$", str(laby[j][i])) or re.match(
                "^[A-Z]*$", str(laby[j][i])
            ):
                # Add a random color, but same color for the same number
                if randomColor:
                    color = hash(str(laby[j][i])) % 255 + 16

                if [j, i] in shortestPath:
                    color = Screen.COLOUR_GREEN

                screen.print_at(
                    f"{laby[j][i]}".center(fixedWidth),
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


def displayShortestPath(screen, maze, goal):
    curPos = goal
    x, y = curPos[0], curPos[1]
    shortestPath = []
    while str(maze[x][y]) != "00":
        shortestPath.append([x, y])

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

        printStep(screen, maze, shortestPath=shortestPath)

    # Color the start
    shortestPath.append([x, y])
    printStep(screen, maze, shortestPath=shortestPath)
    sleep(1)

    # Remove all number except the shortest path
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] != WALL and [i, j] not in shortestPath:
                maze[i][j] = EMPTY

    printStep(screen, maze, shortestPath=shortestPath)


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
    return str(maze[x][y]).isdigit() and str(maze[x][y]) != WALL


def printStep(screen, maze, randomColor=False, shortestPath=[]):
    if screen.has_resized():
        screen.clear()
        screen.refresh()
    # screen.clear()
    # sleep(0.1)
    printLabyrinth(screen, maze, randomColor, shortestPath)
    screen.refresh()
