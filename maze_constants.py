from asciimatics.screen import Screen

# Labyrinth Symbols
EMPTY = "  "
# WALL = "##"
WALL = "##"
VISITED = "**"
BADWAY = "XX"
GOAL = "VV"
START = "SS"
# Define the colors (asciimatics uses integers for colors)
COLOR_MAP = {
    WALL: Screen.COLOUR_WHITE,  # WALL BROWN
    EMPTY: Screen.COLOUR_BLACK,  # EMPTY
    VISITED: Screen.COLOUR_CYAN,  # VISITED
    BADWAY: Screen.COLOUR_RED,  # BADWAY
    GOAL: Screen.COLOUR_MAGENTA,  # GOAL
    START: Screen.COLOUR_GREEN,  # START
}

BLACK_COLOURS = [16, *range(232, 256)]
