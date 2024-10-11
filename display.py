from typing import override
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.exceptions import StopApplication, NextScene
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
    "🐶": Screen.COLOUR_RED,  # START
}


# Helper functions
def checkBounds(maze, x, y):
    sizeX = len(maze)
    sizeY = len(maze[0])
    return x < sizeX and y < sizeY and x >= 0 and y >= 0


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


class LabyrinthEffect(Effect):
    def __init__(self, screen, maze):
        super().__init__(screen)
        self.maze = maze
        self.fixed_width = getFixedWidth(len(maze), len(maze[0]))

    def update_maze(self, maze):
        """Update the maze being rendered."""
        self.maze = maze

    def _print_maze(self, screen):
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])

        # Add walls around the maze
        laby_with_walls = [[WALL] + row + [WALL] for row in self.maze]
        top_bottom_wall_row = [WALL] * (sizeX + 2)
        laby_with_walls = (
            [top_bottom_wall_row] + laby_with_walls + [top_bottom_wall_row]
        )

        sizeX = len(laby_with_walls)
        sizeY = len(laby_with_walls[0])

        fixedWidth = getFixedWidth(sizeX, sizeY)
        screen_width = screen.width
        screen_height = screen.height
        start_x = (screen_width - (sizeY * fixedWidth)) // 2
        start_y = (screen_height - sizeX) // 2

        for i in range(sizeY):
            for j in range(sizeX):
                cell = laby_with_walls[j][i]
                color = COLOR_MAP.get(cell, Screen.COLOUR_WHITE)
                screen.print_at(
                    cell.center(fixedWidth),
                    start_x + j * fixedWidth,
                    start_y + i,
                    colour=color,
                )

    def stop_frame(self):
        """Return the frame number to stop the effect."""
        # Returning None indicates that the effect should run indefinitely.
        return None

    def reset(self):
        pass

    def _update(self, frame_no):
        self._print_maze(self.screen)


class LabyrinthScene(Scene):
    def __init__(self, screen, maze_effect):
        effects = [maze_effect]
        super(LabyrinthScene, self).__init__(effects, -1)


def printStep(screen, maze, maze_effect):
    """Update the maze and refresh the screen."""
    maze_effect.update_maze(maze)
    screen.refresh()
