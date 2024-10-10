import os

from asciimatics.screen import Screen


from generation import (
    generateLabyrinth,
    mergeMazeGeneration,
    clearLabyrinth,
    addRandomStartAndGoal,
)
from display import printLabyrinth


# strLabyrinth = """S■□□□□□
# □■□■■□■
# □■□■⚿□□
# □□□□■■□
# □■□■□□□
# □■□□□■□"""
#
#
# sizeX = strLabyrinth.index("\n")
# sizeY = strLabyrinth.count("\n") + 1


#  Convertit le labyrinthe en tableau 2D, chaque case est un caractère, origine en haut à gauche, lab[sizeX][sizeY]
def convertLabyrinth(strLabyrinth):
    sizeX = strLabyrinth.index("\n")
    sizeY = strLabyrinth.count("\n") + 1
    lab = []
    for i in range(sizeX):
        lab.append([])
        for j in range(sizeY):
            lab[i].append(strLabyrinth[i + j * (sizeX + 1)])
    return lab


def saveLabyrinthToFile(lab, filename="labyrinth.txt"):
    with open(filename, "w") as f:
        for row in lab:
            f.write("".join(row) + "\n")


def Main(screen):
    sizeX = 65
    sizeY = 65

    lab = generateLabyrinth(sizeX, sizeY)
    mergeMazeGeneration(screen, lab, sizeX, sizeY)
    clearLabyrinth(lab)
    [start, goal] = addRandomStartAndGoal(lab, sizeX, sizeY)

    if not start:
        raise ValueError("The 'start' variable is empty or invalid")

    saveLabyrinthToFile(lab)

    pwd = os.getcwd()

    # Wait for the user
    # input("Press Enter to start the simulation...")
    ev = screen.get_key()
    while ev != ord("r"):
        ev = screen.get_key()
    # Escape spaces in path
    pwd = pwd.replace(" ", "\\ ")

    bfs = pwd + "/bfs.py"
    dfs = pwd + "/dfs.py"

    # Run DFS and BFS in different terminal in parallel
    cmd = f"gnome-terminal --maximize -- bash -c 'source {pwd}/.venv/bin/activate; python {bfs} \"{str(start)}\"'"
    os.system(cmd)
    cmd = f"gnome-terminal --maximize -- bash -c 'source {pwd}/.venv/bin/activate; python {dfs} \"{str(start)}\"'"
    os.system(cmd)


if __name__ == "__main__":
    Screen.wrapper(Main)
