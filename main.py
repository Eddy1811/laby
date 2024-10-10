import os
from time import sleep
from display import printLabyrinth

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
    sizeX = 35
    sizeY = 35

    # Common settings for screen
    screen.clear()
    screen.refresh()
    screen.set_title("Maze Solver")

    lab = generateLabyrinth(sizeX, sizeY)
    mergeMazeGeneration(screen, lab, sizeX, sizeY)
    clearLabyrinth(lab)
    [start, goal] = addRandomStartAndGoal(lab, sizeX, sizeY)

    screen.clear()
    printLabyrinth(screen, lab)

    # Escape spaces in start position
    start = str(start).replace(" ", "\\ ")

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

    # Check if Windows Terminal (wt.exe) is installed
    if os.system("wt.exe --version") != 0:
        raise Exception(
            "Windows Terminal (wt.exe) is not installed or not found in PATH"
        )

    # Get current working directory
    pwd = os.getcwd()

    # Define the commands to run DFS and BFS scripts in parallel
    bfs_cmd = f"bash -c 'source {pwd}/.venv/bin/activate && python {bfs} {start}'"
    dfs_cmd = f"bash -c 'source {pwd}/.venv/bin/activate && python {dfs} {start}'"

    # Run DFS and BFS in different Windows Terminal tabs in parallel
    os.system(f"wt.exe -w -1 nt --title 'BFS' {bfs_cmd}")
    os.system(f"wt.exe -w -1 nt --title 'DFS' {dfs_cmd}")

    while True:
        if screen.has_resized():
            screen.clear()
            screen.refresh()
            printLabyrinth(screen, lab)
            sleep(0.1)


if __name__ == "__main__":
    Screen.wrapper(Main)
