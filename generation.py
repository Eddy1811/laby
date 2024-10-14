from random import randint
import re


# Labyrinth Symbols
EMPTY = "▮"
WALL = "🟫"
VISITED = "🐾"
BADWAY = "🍫"
GOAL = "🦴"
START = "🐶"


def printStep(maze, maze_effect, randomColor=False, shortestPath=[]):
    """Update the maze and refresh the screen."""
    maze_effect.update_maze(
        maze,
        randomColor=randomColor,
        shortestPath=shortestPath,
    )


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


def getNorth2(x, y):
    return [x, y - 2]


def getSouth2(x, y):
    return [x, y + 2]


def getEast2(x, y):
    return [x + 2, y]


def getWest2(x, y):
    return [x - 2, y]


def visitEmpty(lab, pos):
    x = pos[0]
    y = pos[1]
    lab[x][y] = VISITED


def checkNotVisited(lab, pos):
    sizeX = len(lab)
    sizeY = len(lab[0])
    x = pos[0]
    y = pos[1]
    if x >= sizeX or y >= sizeY or x < 0 or y < 0:
        return False
    return lab[x][y] == WALL


def checkCaseGen(vec2, maze, width, height):
    if vec2[0] >= width or vec2[1] >= height or vec2[0] < 0 or vec2[1] < 0:
        return False
    return maze[vec2[0]][vec2[1]] != WALL


def generateLabyrinth(width, height):
    # Checkerboard
    maze = []
    emptyCount = 0
    for i in range(width):
        maze.append([])
        for j in range(height):
            if j % 2 == 0 and i % 2 == 0:
                maze[i].append(emptyCount)
                emptyCount += 1
            else:
                maze[i].append(WALL)
    return maze


def generationDone(maze, width, height):
    value = -1
    for i in range(width):
        if maze[i][0] != WALL:
            value = maze[i][0]
            break
    for i in range(width):
        for j in range(height):
            if maze[i][j] != WALL and maze[i][j] != value:
                return False
    return True


def mergeMazeGeneration(maze, width, height, maze_effect):
    posX = -1
    posY = -1
    value = " "
    # screen.clear()
    # Tant que la case n'est pas un chiffre ou qu'il n'y a pas de cases possibles
    # On en cherche une nouvelle
    # On regarde si les cases autour de la case sont de la même valeur
    # Si non, on ajoute les cases possibles
    # On en choisi une aléatoirement
    while not generationDone(maze, width, height):
        possibleCases = []
        while not re.match("^[0-9]*$", str(value)) or len(possibleCases) == 0:
            possibleCases = []
            posX = randint(0, width - 1)
            posY = randint(0, height - 1)
            value = maze[posX][posY]

            north = getNorth2(posX, posY)
            east = getEast2(posX, posY)
            south = getSouth2(posX, posY)
            west = getWest2(posX, posY)

            # Generate probabilities for the directions
            chance = 25
            if checkCaseGen(north, maze, width, height):
                if maze[north[0]][north[1]] != maze[posX][posY]:
                    possibleCases.append(north)
                elif randint(0, 100) < chance:
                    possibleCases.append(north)
            if checkCaseGen(east, maze, width, height):
                if maze[east[0]][east[1]] != maze[posX][posY]:
                    possibleCases.append(east)
                elif randint(0, 100) < chance:
                    possibleCases.append(east)
            if checkCaseGen(south, maze, width, height):
                if maze[south[0]][south[1]] != maze[posX][posY]:
                    possibleCases.append(south)
                elif randint(0, 100) < chance:
                    possibleCases.append(south)
            if checkCaseGen(west, maze, width, height):
                if maze[west[0]][west[1]] != maze[posX][posY]:
                    possibleCases.append(west)
                elif randint(0, 100) < chance:
                    possibleCases.append(west)

        # On choisi une case aléatoire parmis les cases possibles
        nextCase = possibleCases[randint(0, len(possibleCases) - 1)]
        nextX = nextCase[0]
        nextY = nextCase[1]

        # On regarde la différence entre la case actuelle et la case suivante
        diffX = nextX - posX
        diffY = nextY - posY

        wallDeleteX = posX
        wallDeleteY = posY

        # On regarde si on doit supprimer un mur
        if diffX != 0:
            if diffX > 0:
                wallDeleteX = posX + 1
            else:
                wallDeleteX = posX - 1
        if diffY != 0:
            if diffY > 0:
                wallDeleteY = posY + 1
            else:
                wallDeleteY = posY - 1

        # On supprime le mur et on change la valeur de la case TODO
        for x in range(len(maze)):
            for y in range(len(maze[x])):
                case = maze[x][y]
                if (
                    [x, y] != [nextX, nextY]
                    and case == maze[nextX][nextY]
                    and case != WALL
                ):
                    maze[x][y] = value
        maze[nextX][nextY] = value
        maze[wallDeleteX][wallDeleteY] = value

        printStep(maze, maze_effect, randomColor=True)


def clearLabyrinth(lab):
    for i in range(len(lab)):
        for j in range(len(lab[i])):
            if lab[i][j] != WALL and lab[i][j] != START and lab[i][j] != GOAL:
                lab[i][j] = EMPTY


def addRandomStartAndGoal(maze, width, height):
    start = [randint(0, width - 1), randint(0, height - 1)]
    goal = [randint(0, width - 1), randint(0, height - 1)]
    while maze[start[0]][start[1]] == WALL:
        start = [randint(0, width - 1), randint(0, height - 1)]
    while maze[goal[0]][goal[1]] == WALL:
        goal = [randint(0, width - 1), randint(0, height - 1)]
    maze[start[0]][start[1]] = START
    maze[goal[0]][goal[1]] = GOAL
    return [start, goal]


def checkCaseIsDigit(maze, pos):
    x, y = pos[0], pos[1]
    if not checkBounds(maze, x, y):
        return False
    return (str(maze[x][y]).isdigit() or maze[x][y] == VISITED) and str(
        maze[x][y]
    ) != WALL


def displayShortestPath(maze, goal, maze_effect):
    curPos = goal
    x, y = curPos[0], curPos[1]
    shortestPath = []
    while str(maze[x][y]) != "0" or maze[x][y] == START:
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
            return

        x, y = nextCase[0], nextCase[1]

        printStep(maze, maze_effect=maze_effect, shortestPath=shortestPath)
    return shortestPath
