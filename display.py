from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, Layout, Label, Text, Button, Divider
from asciimatics.exceptions import StopApplication
from generation import (
    generateLabyrinth,
    mergeMazeGeneration,
    clearLabyrinth,
    addRandomStartAndGoal,
    displayShortestPath,
)
from solver import BFS, DFS
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


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


class MazeInputFrame(Frame):
    def __init__(self, screen, input_data):
        super(MazeInputFrame, self).__init__(
            screen,
            screen.height // 2,
            screen.width // 2,
            has_border=True,
            name="Maze Input Form",
        )

        self.set_theme("bright")

        # Initialize self.data to store the width and height
        self.data = {"width": "", "height": ""}
        self.input_data = (
            input_data  # Reference to external dictionary to store final input
        )

        # Layout to organize widgets
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        # Add widgets to the layout
        self.message_label = Label("")
        layout.add_widget(self.message_label)

        layout.add_widget(Label("Enter maze width (odd number >= 5):"))
        self.width_input = Text("Width:", "width")
        layout.add_widget(self.width_input)

        layout.add_widget(Label("Enter maze height (odd number >= 5):"))
        self.height_input = Text("Height:", "height")
        layout.add_widget(self.height_input)

        # Button to submit the form
        layout.add_widget(Button("Submit", self._submit))

        # Finalize layout
        self.fix()

    def _submit(self):
        # Save the input data
        self.save()

        try:
            # Check if the self.data is None
            if not self.data:
                self.message_label.text = (
                    "Please enter valid integers for width and height!"
                )
                self.screen.force_update()
                return

            # Retrieve width and height and validate them
            width = int(self.data["width"])
            height = int(self.data["height"])

            if width < 5 or width % 2 == 0:
                self.message_label.text = "Width must be an odd number >= 5!"
                self.screen.force_update()
                return

            if height < 5 or height % 2 == 0:
                self.message_label.text = "Height must be an odd number >= 5!"
                self.screen.force_update()
                return

            # If input is valid, store it in the external dictionary
            self.input_data["width"] = width
            self.input_data["height"] = height
            # If input is valid, print the values and exit the form
            print(f"Maze width: {width}, Maze height: {height}")
            raise StopApplication("Maze dimensions entered successfully")

        except ValueError:
            # Handle non-integer input
            self.message_label.text = (
                "Please enter valid integers for width and height!"
            )
            self.screen.force_update()


class SolverMenuFrame(Frame):
    def __init__(self, screen, sizeX, sizeY):
        lab = generateLabyrinth(sizeX, sizeY)
        super(SolverMenuFrame, self).__init__(
            screen, screen.height, screen.width, has_border=True
        )
        self.set_theme("bright")
        self.maze = lab
        self.generator = None
        self.BFS = False
        self.DFS = False
        self.shortestPath = []

        # Layout for menu options
        layout = Layout([1])
        self.add_layout(layout)

        self.message_label = Label("Select the algorithm to run:")
        layout.add_widget(self.message_label)

        # Buttons to select BFS and DFS
        layout.add_widget(Button("Run Generation", self.run_generation))
        layout.add_widget(Button("Run BFS", self.run_bfs))
        layout.add_widget(Button("Run DFS", self.run_dfs))
        layout.add_widget(Button("Quit", self.quit))

        # Maze display
        layout.add_widget(Divider())
        layout.add_widget(Label("Maze:"))

        self.fix()

    def _update(self, frame_no):
        # Update the maze display
        super(SolverMenuFrame, self)._update(frame_no)
        self._print_maze(self._screen)

    def update_maze(
        self, maze, randomColor=False, BFS=False, DFS=False, shortestPath=[]
    ):
        """Update the maze being rendered."""
        self.maze = maze
        self._print_maze(self._screen, randomColor)
        self._screen.refresh()

    def _print_maze(self, screen, randomColor=False):
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

                # Handle cases where the cell contains a number or letter
                if re.match("^[0-9]*$", str(cell)) or re.match("^[A-Z]*$", str(cell)):
                    # Add a random color, but same color for the same number
                    if randomColor:
                        color = hash(str(cell)) % 255 + 16

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
                    # Remove spaces from the start and goal only to test
                    cellWithoutSpaces = str(cell).replace(" ", "")
                    if cellWithoutSpaces == "0" and not randomColor:
                        cell = START
                    screen.print_at(
                        f"{cell}".center(fixedWidth),
                        start_x + j * fixedWidth,
                        start_y + i,
                        colour=color,
                    )
                else:
                    # Get the corresponding character and color
                    screen.print_at(
                        cell.center(fixedWidth),
                        start_x + j * fixedWidth,
                        start_y + i,
                        colour=color,
                    )

    def run_generation(self):
        # Generate the maze
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])

        mergeMazeGeneration(self.maze, sizeX, sizeY, self)

        [start, goal] = addRandomStartAndGoal(self.maze, sizeX, sizeY)
        clearLabyrinth(self.maze)
        self.start = start
        self.goal = goal
        clearLabyrinth(self.maze)

    def run_bfs(self):
        # Run the BFS algorithm
        clearLabyrinth(self.maze)
        self.BFS = True
        self.DFS = False
        self.shortestPath = []

        # check if self.start is defined
        if not hasattr(self, "start"):
            [start, goal] = addRandomStartAndGoal(
                self.maze, len(self.maze), len(self.maze[0])
            )
            self.start = start

        BFS(self.screen, self.maze, maze_effect=self, start=self.start)

        sleep(2)  # Wait a moment to let user see the output

        self.shortestPath = displayShortestPath(self.maze, self.goal, maze_effect=self)

    def run_dfs(self):
        self.DFS = True
        self.BFS = False
        self.shortestPath = []

        clearLabyrinth(self.maze)
        # check if self.start is defined
        if not hasattr(self, "start"):
            [start, goal] = addRandomStartAndGoal(
                self.maze, len(self.maze), len(self.maze[0])
            )
            self.start = start

        # Run the DFS algorithm
        DFS(self.screen, self.maze, self, self.start)

    def quit(self):
        raise StopApplication("User chose to quit")


# Scene that combine the maze and the solver menu to be displayed
class MazeSolverScene(Scene):
    def __init__(self, screen, sizeX, sizeY):
        # Split the screen into two parts
        effects = [SolverMenuFrame(screen, sizeX, sizeY)]

        super(MazeSolverScene, self).__init__(effects, -1, name="Maze Solver Scene")
