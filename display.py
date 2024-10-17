from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, Label, Text, Button, Divider
from asciimatics.exceptions import StopApplication
from generation import (
    generateLabyrinth,
    mergeMazeGeneration,
    clear_maze,
    append_start_and_goal,
)
from maze_widget import MazeWidget
from solver import BFS, DFS, compute_shortest_path
import time
import os
from collections import deque
from threading import Thread


# Function to get terminal size
def get_terminal_size():
    return os.get_terminal_size()


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

            if width < 5:
                self.message_label.text = "Width must be an odd number >= 5!"
                self.screen.force_update()
                return

            if height < 5:
                self.message_label.text = "Height must be an odd number >= 5!"
                self.screen.force_update()
                return

            # If input is valid, store it in the external dictionary
            self.input_data["width"] = width
            self.input_data["height"] = height
            # If input is valid, print the values and exit the form
            print(f"Maze width: {width}, Maze height: {height}")
            raise StopApplication("User submitted the form")

        except ValueError:
            # Handle non-integer input
            self.message_label.text = (
                "Please enter valid integers for width and height!"
            )
            self.screen.force_update()


class SolverMenuFrame(Frame):
    def __init__(self, screen, sizeX, sizeY):
        super(SolverMenuFrame, self).__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            name="Maze Solver",
        )
        self.set_theme("bright")
        self.maze = generateLabyrinth(sizeX, sizeY)
        self.generator = None
        self.BFS = False
        self.DFS = False
        self.shortestPath = []
        self.last_screen_size = get_terminal_size()
        self.buffer_iterator = 0

        # Layout for menu options
        self.layout = Layout([2])

        self.add_layout(self.layout)

        self.message_label = Label("Select the algorithm to run:")
        self.layout.add_widget(self.message_label, 0)

        # Buttons to select BFS and DFS
        self.layout.add_widget(Button("Run Generation", self.run_generation), 0)
        self.layout.add_widget(
            Button("New Start and Goal", self.run_place_start_and_goal), 0
        )
        self.layout.add_widget(Button("Run BFS", self.run_bfs), 0)
        self.layout.add_widget(Button("Run DFS", self.run_dfs), 0)
        self.layout.add_widget(Button("Quit", self.quit), 0)

        self.maze_widget = MazeWidget(self.maze, sizeX, sizeY)
        # Maze display
        self.layout.add_widget(Divider(), 0)
        self.layout.add_widget(Label("Maze:"), 0)
        self.layout.add_widget(self.maze_widget, 0)
        self.fix()

    def _update(self, frame_no):
        # self.update_maze(self.maze, randomColor=False, shortestPath=self.shortestPath)
        if self._screen.has_resized():
            self.screen.clear()
            self.screen.force_update(full_refresh=True)
            self.screen.refresh()
            self.fix()
            self.last_screen_size = get_terminal_size()
        if self.maze_widget.needs_update:
            self.maze_widget.update(frame_no)
            self.screen.refresh()
        super(SolverMenuFrame, self)._update(frame_no)

    def update_maze(self, maze, randomColor=False, shortestPath=[]):
        """Update the maze being rendered."""
        if shortestPath:
            self.shortestPath = shortestPath

        self.maze_widget.BFS = self.BFS
        self.maze_widget.shortest_path = shortestPath
        self.maze_widget.random_color = randomColor

        self.maze_widget.save_interval = (len(self.maze) * len(self.maze[0])) // 100
        if self.maze_widget.save_interval == self.maze_widget.buffer_size:
            self.save_interval = 1

        if (
            self.buffer_iterator % self.maze_widget.save_interval == 0
            or self.BFS
            or self.DFS
        ):
            self.maze_widget.compute(maze)

        self.buffer_iterator += 1

    def run_generation(self):
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])
        self.maze_widget.needs_update = False

        self.BFS = False
        self.DFS = False
        self.shortestPath = []
        # self.update_maze(self.maze, randomColor=True, shortestPath=[])
        # self.maze_widget.update(0)
        self.maze = generateLabyrinth(sizeX, sizeY)
        mergeMazeGeneration(self.maze, sizeX, sizeY, self)

        [start, goal] = append_start_and_goal(self.maze, sizeX, sizeY)
        self.start = start
        self.goal = goal
        clear_maze(self.maze)

        self.update_maze(self.maze)
        self.maze_widget.compute(self.maze)

        self.maze_widget.update_thread()

    def run_place_start_and_goal(self):
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])
        self.maze_widget.needs_update = False
        self.BFS = False
        self.DFS = False
        self.shortestPath = []
        self.update_maze(self.maze, randomColor=True, shortestPath=[])
        clear_maze(self.maze, True)
        [start, goal] = append_start_and_goal(self.maze, sizeX, sizeY)
        self.start = start
        self.goal = goal
        self.update_maze(self.maze)
        self.maze_widget.compute(self.maze)
        self.maze_widget.update_thread()

    def run_bfs(self):
        # Run the BFS algorithm
        clear_maze(self.maze)
        self.BFS = True
        self.DFS = False
        self.shortestPath = []
        self.maze_widget.needs_update = False
        self.update_maze(self.maze)

        BFS(self.maze, maze_effect=self, start=self.start)

        self.shortestPath = compute_shortest_path(
            self.maze, self.goal, maze_effect=self
        )

        self.maze_widget.compute(self.maze)
        time.sleep(2)
        self.maze_widget.update_thread()

    def run_dfs(self):
        self.DFS = True
        self.BFS = False
        self.shortestPath = []
        self.update_maze(self.maze)
        self.maze_widget.needs_update = False

        # Run the DFS algorithm
        DFS(self.maze, self, self.start)
        self.maze_widget.compute(self.maze)
        self.maze_widget.update_thread()

    def quit(self):
        raise StopApplication("User chose to quit")


# Scene that combine the maze and the solver menu to be displayed
class MazeSolverScene(Scene):
    def __init__(self, screen, sizeX, sizeY, effects=None):
        # Split the screen into two parts
        effects = effects or [SolverMenuFrame(screen, sizeX, sizeY)]

        super(MazeSolverScene, self).__init__(effects, -1, name="Maze Solver Scene")

    def create_effects(self, screen, sizeX, sizeY):
        return [SolverMenuFrame(screen, sizeX, sizeY)]
