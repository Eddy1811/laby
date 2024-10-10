from asciimatics.screen import Screen
from solver import DFS
import sys
from time import sleep
from display import printLabyrinth


def readLabyrinthFromFile(filename="labyrinth.txt"):
    with open(filename, "r") as f:
        lab = [list(line.strip()) for line in f.readlines()]
    return lab


def convertStringToPosition(position_str):
    # Remove square brackets and spaces, then split by comma
    position_str = position_str.strip("[]")
    x, y = map(int, position_str.split(","))
    return [x, y]


def runDFS(screen):
    screen.clear()
    lab = readLabyrinthFromFile()
    start = sys.argv[1]
    start = convertStringToPosition(start)
    DFS(screen, lab, start)
    while True:
        if screen.has_resized():
            screen.clear()
            screen.refresh()
            printLabyrinth(screen, lab)
            sleep(0.1)


if __name__ == "__main__":
    input("Press Enter to start the simulation...")
    Screen.wrapper(runDFS)
