from asciimatics.screen import Screen
from solver import BFS
import sys


def readLabyrinthFromFile(filename="labyrinth.txt"):
    with open(filename, "r") as f:
        lab = [list(line.strip()) for line in f.readlines()]
    return lab


def convertStringToPosition(position_str):
    # Remove square brackets and spaces, then split by comma
    position_str = position_str.strip("[]")
    x, y = map(int, position_str.split(","))
    return [x, y]


def runBFS(screen):
    lab = readLabyrinthFromFile()
    start = sys.argv[1]
    start = convertStringToPosition(start)

    path = []

    ev = screen.get_key()
    while ev != ord("q"):
        ev = screen.get_key()
    BFS(screen, lab, start)

    ev = screen.get_key()
    while ev != ord("q"):
        ev = screen.get_key()


if __name__ == "__main__":
    Screen.wrapper(runBFS)
