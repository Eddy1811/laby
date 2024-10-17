from asciimatics.widgets import Frame, Layout, Label, Button, Divider
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


# Function to get terminal size
def get_terminal_size():
    return os.get_terminal_size()


def getFixedWidth(width, height):
    totalSize = width * height
    return len(str(totalSize))


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
