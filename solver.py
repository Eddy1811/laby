# Labyrinth Symbols
EMPTY = "▮"
WALL = "🟫"
VISITED = "🐾"
BADWAY = "🍫"
GOAL = "🦴"
START = "🐶"


def printStep(screen, maze, maze_effect, shortestPath=[], randomColor=False):
    """Update the maze and refresh the screen."""
    maze_effect.update_maze(maze, randomColor=randomColor, shortestPath=shortestPath)


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


def checkCase(maze, x, y):
    return maze[x][y] == EMPTY


def checkCaseVec(maze, vec2):
    if not checkBounds(maze, vec2[0], vec2[1]):
        return False
    return maze[vec2[0]][vec2[1]] == EMPTY or maze[vec2[0]][vec2[1]] == GOAL


def visit(maze, pos, step):
    # if step < 10:
    #    step = f"0{step}"
    maze[pos[0]][pos[1]] = step


def badWay(maze, pos):
    x = pos[0]
    y = pos[1]
    maze[x][y] = BADWAY


path = []


# def DFS_recurse(maze, start=[0, 0], step=0):
#    curPos = start
#    x = curPos[0]
#    y = curPos[1]
#
#    maze_effect = LabyrinthEffect(screen, maze)
#    if step == 0:
#        visit(maze, curPos, step)
#        step += 1
#        path.append(curPos)
#        printStep(maze, path, maze_effect)
#
#    if checkCaseVec(maze, getNorth(x, y)):
#        nextCase = getNorth(x, y)
#    elif checkCaseVec(maze, getEast(x, y)):
#        nextCase = getEast(x, y)
#    elif checkCaseVec(maze, getSouth(x, y)):
#        nextCase = getSouth(x, y)
#    elif checkCaseVec(maze, getWest(x, y)):
#        nextCase = getWest(x, y)
#    else:
#        badWay(maze, curPos)
#        path.pop()
#        printStep(screen, maze, maze_effect)
#        DFS(maze, path[len(path) - 1], step)
#        return
#
#    if maze[nextCase[0]][nextCase[1]] == GOAL:
#        visit(maze, nextCase, step)
#        path.append(nextCase)
#        # print("WIN")
#        # print("Longueur du chemin trouvé: ", len(path))
#        return
#
#    path.append(nextCase)
#    visit(maze, nextCase, step)
#    printStep(screen, maze, maze_effect)
#
#    DFS(maze, nextCase, step + 1)


# Non récursif
def DFS(screen, maze, maze_effect, start=[0, 0], step=0):
    curPos = start
    x = curPos[0]
    y = curPos[1]

    path = []
    if step == 0:
        visit(maze, curPos, step)
        step += 1
        path.append(curPos)
        printStep(screen, maze, maze_effect)

    while maze[x][y] != GOAL:
        x = curPos[0]
        y = curPos[1]

        if checkCaseVec(maze, getNorth(x, y)):
            nextCase = getNorth(x, y)
        elif checkCaseVec(maze, getEast(x, y)):
            nextCase = getEast(x, y)
        elif checkCaseVec(maze, getSouth(x, y)):
            nextCase = getSouth(x, y)
        elif checkCaseVec(maze, getWest(x, y)):
            nextCase = getWest(x, y)
        else:
            badWay(maze, curPos)
            path.pop()
            printStep(screen, maze, maze_effect)
            step += 1
            if len(path) == 0:
                raise Exception("No solution")
            curPos = path[len(path) - 1]
            continue

        if maze[nextCase[0]][nextCase[1]] == GOAL:
            # visit(maze, nextCase, step)
            path.append(nextCase)
            # print("WIN")
            # print("Longueur du chemin trouvé: ", len(path) - 1)
            return

        path.append(nextCase)
        visit(maze, nextCase, step)
        printStep(screen, maze, maze_effect)
        step += 1
        curPos = nextCase


def BFS(screen, maze, maze_effect, start=[0, 0], step=0):
    queue = []
    screen.force_update()

    queue.append(start)
    while queue:
        curPos = queue.pop(0)

        while (
            str(maze[curPos[0]][curPos[1]]).isdigit()
            or maze[curPos[0]][curPos[1]] == VISITED
        ):
            curPos = queue.pop(0)

        x = curPos[0]
        y = curPos[1]
        if maze[x][y] == GOAL:
            # print("WIN")
            # print("Longueur du chemin trouvé: ", step)
            # visit(maze, curPos, step)
            printStep(screen, maze, maze_effect=maze_effect)

            # displayShortestPath(screen, maze, curPos, path)
            # Return goal coordinates
            # return curPos
            return
        if checkCaseVec(maze, getNorth(x, y)):
            nextCase = getNorth(x, y)
            queue.append(nextCase)
        if checkCaseVec(maze, getEast(x, y)):
            nextCase = getEast(x, y)
            queue.append(nextCase)
        if checkCaseVec(maze, getSouth(x, y)):
            nextCase = getSouth(x, y)
            queue.append(nextCase)
        if checkCaseVec(maze, getWest(x, y)):
            nextCase = getWest(x, y)
            queue.append(nextCase)
        visit(maze, curPos, step)
        printStep(screen, maze, maze_effect)
        step += 1
