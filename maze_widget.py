from asciimatics.widgets import Widget
from asciimatics.screen import Screen
from collections import deque
import time
import os
import math
import random
from threading import Thread


from maze_constants import WALL, VISITED, START, COLOR_MAP, EMPTY


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


def rgb_to_ansi(r, g, b):
    """
    Converts an RGB color to the nearest ANSI 256 color code.
    """
    # Normalize RGB to a 0-5 range for the 6x6x6 color cube
    r_norm = int((r / 255) * 5)
    g_norm = int((g / 255) * 5)
    b_norm = int((b / 255) * 5)

    return 16 + (36 * r_norm) + (6 * g_norm) + b_norm


def create_gradient(base_color, steps=10):
    """
    Creates a gradient from the brightest to the darkest color based on the base RGB color.

    Parameters:
    - base_color: tuple (R, G, B), e.g., (255, 0, 0) for red.
    - steps: The number of gradient steps from brightest to darkest.

    Returns:
    - A list of ANSI color codes for the gradient.
    """
    r, g, b = base_color
    gradient_colors = []

    # Generate gradient by darkening the base color in steps
    for i in range(steps):
        factor = (steps - i) / steps  # Gradually reduce brightness
        r_step = math.floor(r * factor)
        g_step = math.floor(g * factor)
        b_step = math.floor(b * factor)

        ansi_code = rgb_to_ansi(r_step, g_step, b_step)
        gradient_colors.append(ansi_code)

    # Remove black from gradient
    for i in range(len(gradient_colors)):
        if gradient_colors[i] in [16, 232, 233, 234, 235, 236]:
            gradient_colors.pop(i)
            break
    # remove duplicates
    gradient_colors = list(dict.fromkeys(gradient_colors + gradient_colors[::-1]))

    return gradient_colors


def get_color_from_percentage(gradient_colors, percentage, exponent=2):
    """
    Gets the corresponding color from the gradient based on an exponentially scaled percentage.

    Parameters:
    - gradient_colors: List of ANSI color codes for the gradient.
    - percentage: A float value between 0 and 100 representing the desired color's position in the gradient.
    - exponent: The exponent to apply to the percentage for exponential scaling (default: 2).

    Returns:
    - The ANSI color code corresponding to the exponentially scaled percentage.
    """
    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100.")

    # Normalize percentage between 0 and 1
    normalized_percentage = percentage / 100.0

    # Apply exponential scaling
    scaled_percentage = normalized_percentage**exponent

    # Convert scaled percentage back to 0-100 range
    scaled_percentage *= 100

    # Map the scaled percentage to the index in the gradient
    steps = len(gradient_colors)
    index = int((scaled_percentage / 100) * (steps - 1))

    return gradient_colors[index]


def print_gradient(gradient_colors):
    """
    Print the gradient colors in the terminal using ANSI escape codes.
    """
    for ansi_color in gradient_colors:
        print(f"\033[48;5;{ansi_color}m  \033[0m", end="")
    print()  # Newline after printing the gradient


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
        super(MazeWidget, self).__init__(name, tab_stop=False)
        self._maze = maze
        self._required_height = height
        self._required_width = width
        self.random_color = randomColor
        self.BFS = BFS
        self.shortest_path = shortestPath or []

        self.needs_update = True
        self.buffer_length = 0

        self.frame_no = 0
        self.start_time = time.time()

        ## Buffer settings
        # Buffer to store the frames
        # Size is influenced by the size of the maze and the max_fps
        # The more complex the maze, the bigger the buffer
        # The higher the max_fps, the smaller the buffer
        overload_factor = (
            1.1  # adjust this factor to control the level of buffer overload
        )

        self.buffer_size = int(
            (height * width) ** 0.5 / (max_fps**0.5 + 1) * overload_factor
        )
        self.buffer = deque(maxlen=self.buffer_size)

        # The interval to save the maze in the buffer
        # The higher the interval, the more frames are skipped
        # Influenced by the size of the maze and the max
        self.save_interval = (len(maze) * len(maze[0])) // (max_fps * 2)

        if self.save_interval % self.buffer_size == 0:
            self.save_interval = 1

        self.buffer_length = 0
        self.max_fps = max_fps

        self.noSpaces = True

        self.last_maze = None

    def update_thread(self):
        if hasattr(self, "thread") and self.thread is not None:
            if self.thread.is_alive():
                time.sleep(1 / self.max_fps)
                return
            self.thread = Thread(target=self.update, args=(self.frame_no,))
            self.thread.start()
        else:
            self.thread = Thread(target=self.update, args=(self.frame_no,))
            self.thread.start()
        time.sleep(1 / self.max_fps)

    def compute(self, maze):
        # Compute the maze all at once and store the result in the buffer
        copy = [row[:] for row in maze]
        shortest_path = [row[:] for row in self.shortest_path]
        self.buffer.append([copy, [self.random_color, self.BFS, shortest_path]])
        # Dump the buffer if it's full
        # Use another thread to update the screen
        if len(self.buffer) == self.buffer_size:
            self.update_thread()

    def update(self, frame_no):
        # Draw the current frame from the buffer
        self.buffer_length = (
            len(self.buffer) if len(self.buffer) != 0 else self.buffer_length
        )
        while self.buffer:
            # Depending on maze size, we might need to skip some frames

            self.last_maze = self.buffer.popleft()
            self.last_settings = self.last_maze[1]
            self.last_maze = self.last_maze[0]
            self.random_color = self.last_settings[0]
            self.BFS = self.last_settings[1]
            self.shortest_path = self.last_settings[2]
            self._draw(self.last_maze)

            self._frame.canvas.print_at(
                f"Buffer length: {len(self.buffer)}".center(30),
                10,
                5,
                colour=Screen.COLOUR_WHITE,
                bg=Screen.COLOUR_BLACK,
            )
            self._frame.canvas.print_at(
                f"Buffer max size: {self.buffer_size}".center(30),
                10,
                6,
                colour=Screen.COLOUR_WHITE,
                bg=Screen.COLOUR_BLACK,
            )
            self._frame.canvas.print_at(
                f"Save interval: {self.save_interval}".center(30),
                10,
                7,
                colour=Screen.COLOUR_WHITE,
                bg=Screen.COLOUR_BLACK,
            )
            # Sleep to control the speed of the animation
            # use buffer length to adjust the speed
            self.frame.canvas.refresh()
            self._frame.screen.refresh()
            sleep_time = 1 / self.max_fps
            time.sleep(sleep_time)

        # If the buffer is empty, draw
        # the last maze
        if not self.buffer and self.last_maze is not None:
            self._draw(self.last_maze)
            self._frame.canvas.refresh()
            self._frame.screen.refresh()
            # time.sleep(1 / self.max_fps)
        elif not self.buffer:
            self._draw(self._maze)

        self.thread = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def _draw_cell(
        self, fixedWidth, y, x, laby_with_walls, sizeX, sizeY, start_x, start_y
    ):
        cell = laby_with_walls[x][y]
        color = COLOR_MAP.get(cell, Screen.COLOUR_BLACK)

        # Handle cases where the cell contains a number or letter
        if str(cell).isdigit():
            color = COLOR_MAP.get(VISITED, Screen.COLOUR_BLACK)
            # Add a random color, but same color for the same number
            if self.random_color:
                possible_colours = [c for c in range(17, 231)]

                color = possible_colours[hash(str(cell)) % 214]
                if cell == 0:
                    color = Screen.COLOUR_BLACK

            # If BFS is running, color the visited cells, from yellow to red, the farther the redder
            if self.BFS and (cell == VISITED or str(cell).isdigit() or cell == EMPTY):
                # Change color based on the scale
                # the greater is the number, the redder is the color
                # based on percentage of buffer done
                if self.buffer_length != 0:
                    percentage = int(cell) / (sizeX * sizeY)
                else:
                    percentage = 1
                percentage = (1 - percentage) * 100
                if percentage < 0:
                    percentage = 0

                # check if terminal supports 256 colors
                if (
                    os.getenv("TERM") == "xterm-256color"
                    or os.getenv("TERM") == "tmux-256color"
                ):
                    # From brightest to darkest (purple to red)
                    purple = (255, 0, 255)
                    red = (255, 0, 0)
                    blue = (0, 0, 255)
                    cyan = (0, 255, 255)
                    brown = (165, 42, 42)
                    orange = (255, 165, 0)
                    green = (0, 255, 0)
                    yellow = (255, 255, 0)

                    gradient_colors = create_gradient(green)

                    # invert the gradient colors
                    gradient_colors = gradient_colors[::-1]

                    # Gradient_colors : brightest = index 0, darkest = index -1
                    color = get_color_from_percentage(gradient_colors, percentage, 4)

                else:
                    if percentage < 10:
                        color = Screen.COLOUR_MAGENTA
                    elif percentage < 25:
                        color = Screen.COLOUR_RED
                    elif percentage < 66:
                        color = Screen.COLOUR_YELLOW
                    else:
                        color = Screen.COLOUR_CYAN

            if self.shortest_path and [x, y] in self.shortest_path:
                time.sleep(10)
                color = Screen.COLOUR_GREEN
                cell = VISITED

            cellWithoutSpaces = str(cell).replace(" ", "")

            if (
                cellWithoutSpaces == "0"
                and not self.random_color
                and cellWithoutSpaces != VISITED
            ):
                cell = START

            if cell == START:
                self._frame.canvas.print_at(
                    f"{START}".center(fixedWidth),
                    start_x + x * fixedWidth,
                    start_y + y,
                    colour=color,
                )
            else:
                self._frame.canvas.print_at(
                    f"{EMPTY}".center(fixedWidth),
                    start_x + x * fixedWidth,
                    start_y + y,
                    colour=color,
                    bg=color,
                )
        else:
            if sizeX % 2 == 0:
                if x < sizeX - 1:
                    self._frame.canvas.print_at(
                        f"{EMPTY}".center(fixedWidth),
                        start_x + x * fixedWidth,
                        start_y + y,
                        colour=color,
                        bg=color,
                    )
            elif sizeY % 2 == 0:
                if y < sizeY - 1:
                    self._frame.canvas.print_at(
                        f"{EMPTY}".center(fixedWidth),
                        start_x + x * fixedWidth,
                        start_y + y,
                        colour=color,
                        bg=color,
                    )
            else:
                self._frame.canvas.print_at(
                    f"{EMPTY}".center(fixedWidth),
                    start_x + x * fixedWidth,
                    start_y + y,
                    colour=color,
                    bg=color,
                )

    def _draw(self, maze):
        sizeX = len(maze)
        sizeY = len(maze[0])

        if sizeY % 2 != 0:
            laby_with_walls = [[WALL] + row + [WALL] for row in maze]
            top_bottom_wall_row = [WALL] * (sizeY + 2)
        else:
            laby_with_walls = [[WALL] + row for row in maze]
            top_bottom_wall_row = [WALL] * (sizeY + 1)

        laby_with_walls = (
            [top_bottom_wall_row] + laby_with_walls + [top_bottom_wall_row]
        )

        sizeX = len(laby_with_walls)
        sizeY = len(laby_with_walls[0])

        fixedWidth = getFixedWidth(sizeX, sizeY)
        if self.noSpaces:
            fixedWidth = 2
        start_x = (self._frame.canvas.width - (sizeX * fixedWidth)) // 2
        start_y = (self._frame.canvas.height - sizeY) // 2

        for i in range(sizeY):
            for j in range(sizeX):
                self._draw_cell(
                    fixedWidth, i, j, laby_with_walls, sizeX, sizeY, start_x, start_y
                )

    def reset(self):
        pass

    def process_event(self, event):
        return event

    def required_height(self, offset, width):
        return self._required_height

    def required_width(self, offset, w, h, options):
        return self._required_width
