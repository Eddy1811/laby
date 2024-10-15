from asciimatics.widgets import Widget
from asciimatics.screen import Screen
import time


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


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


class MazeWidget(Widget):
    def __init__(
        self,
        maze,
        height,
        width,
        max_fps=60,
        name=None,
        randomColor=False,
        BFS=False,
        shortestPath=None,
    ):
        super(MazeWidget, self).__init__(name)
        self._maze = maze
        self._required_height = height
        self._required_width = width
        self.randomColor = randomColor
        self.BFS = BFS
        self.shortestPath = shortestPath or []

        self.needs_update = True
        self.buffer_length = 0

        self.frame_no = 0
        self.start_time = time.time()
        self.buffer = []
        self.settings_buffer = []
        self.max_fps = max_fps

        self.last_maze = None

    def compute(self, maze):
        # Compute the maze all at once and store the result in the buffer
        copy = [row[:] for row in maze]
        self.buffer.append(copy)
        self.settings_buffer.append([self.randomColor, self.BFS, self.shortestPath])

    def update(self, frame_no):
        # Draw the current frame from the buffer
        while self.buffer:
            # Depending on maze size, we might need to skip some frames
            divider = len(self._maze) // 4
            toSkip = len(self.buffer) // 100
            if self.frame_no % (toSkip + 1) == 0:
                self.last_settings = self.settings_buffer.pop(0)
                self.randomColor = self.last_settings[0]
                self.BFS = self.last_settings[1]
                self.shortestPath = self.last_settings[2]
                self.last_maze = self.buffer.pop(0)
                self._draw(self.last_maze)
                self._frame.canvas.refresh()
                self._frame.screen.refresh()
                # time.sleep(1 / self.max_fps)
                time.sleep(1 / self.max_fps)
            else:
                self.buffer.pop(0)
                self.settings_buffer.pop(0)
            self.frame_no += 1

        if not self.buffer and self.last_maze is not None:
            self._draw(self.last_maze)
            self._frame.canvas.refresh()
            self._frame.screen.refresh()
            # time.sleep(1 / self.max_fps)
        elif not self.buffer:
            self._draw(self._maze)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def _draw(self, maze):
        sizeX = len(maze)
        sizeY = len(maze[0])
        laby_with_walls = [[WALL] + row + [WALL] for row in maze]
        top_bottom_wall_row = [WALL] * (sizeY + 2)
        laby_with_walls = (
            [top_bottom_wall_row] + laby_with_walls + [top_bottom_wall_row]
        )

        sizeX = len(laby_with_walls)
        sizeY = len(laby_with_walls[0])

        fixedWidth = getFixedWidth(sizeX, sizeY)
        start_x = (self._frame.canvas.width - (sizeY * fixedWidth)) // 2
        start_y = (self._frame.canvas.height - sizeX) // 2

        for i in range(sizeY):
            for j in range(sizeX):
                cell = laby_with_walls[j][i]
                color = COLOR_MAP.get(cell, Screen.COLOUR_WHITE)

                # Handle cases where the cell contains a number or letter
                if str(cell).isdigit():
                    # Add a random color, but same color for the same number
                    if self.randomColor:
                        color = hash(str(cell)) % 255 + 16
                        if cell == 0:
                            color = Screen.COLOUR_GREEN

                    # If BFS is running, color the visited cells, from yellow to red, the farther the redder
                    if self.BFS and (cell == VISITED or str(cell).isdigit()):
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

                    if self.shortestPath and [j, i] in self.shortestPath:
                        color = Screen.COLOUR_GREEN
                        cell = VISITED

                    cellWithoutSpaces = str(cell).replace(" ", "")

                    if (
                        cellWithoutSpaces == "0"
                        and not self.randomColor
                        and cellWithoutSpaces != VISITED
                    ):
                        cell = START

                    self._frame.canvas.print_at(
                        f"{cell}".center(fixedWidth),
                        start_x + j * fixedWidth,
                        start_y + i,
                        colour=color,
                    )
                else:
                    # Get the corresponding character and color
                    if 0 <= j < sizeY - 1:
                        self._frame.canvas.print_at(
                            cell * fixedWidth,
                            start_x + j * fixedWidth,
                            start_y + i,
                            colour=color,
                        )
                    elif j == sizeY - 1:
                        self._frame.canvas.print_at(
                            cell * 2,
                            start_x + j * fixedWidth,
                            start_y + i,
                            colour=color,
                        )
                    else:
                        self._frame.canvas.print_at(
                            cell,
                            start_x + j * fixedWidth,
                            start_y + i,
                            colour=color,
                        )

    def reset(self):
        pass

    def process_event(self, event):
        return event

    def required_height(self, offset, width):
        return self._required_height

    def required_width(self, offset, w, h, options):
        return self._required_width
