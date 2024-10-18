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
from asciimatics.screen import Screen


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

    def print_infos(self):
        self.canvas.print_at(
            f"Buffer length: {len(self.maze_widget.buffer)}".center(30),
            10,
            2,
            colour=Screen.COLOUR_WHITE,
            bg=Screen.COLOUR_BLACK,
        )
        self.canvas.print_at(
            f"Buffer max size: {self.maze_widget.buffer_size}".center(30),
            10,
            3,
            colour=Screen.COLOUR_WHITE,
            bg=Screen.COLOUR_BLACK,
        )
        self.canvas.print_at(
            f"Save interval: {self.maze_widget.save_interval}".center(30),
            10,
            4,
            colour=Screen.COLOUR_WHITE,
            bg=Screen.COLOUR_BLACK,
        )
        self.canvas.print_at(
            f"Total frames: {self.maze_widget.total_frames}".center(30),
            10,
            5,
            colour=Screen.COLOUR_WHITE,
            bg=Screen.COLOUR_BLACK,
        )

    def _update(self, frame_no):
        if (
            hasattr(self.maze_widget, "thread")
            and self.maze_widget.thread is not None
            and self.maze_widget.thread.is_alive()
        ):
            return
        super(SolverMenuFrame, self)._update(frame_no)

    def update_maze(self, maze, randomColor=False, shortestPath=[], queue_size=0):
        """Update the maze being rendered."""
        self.set_shortest_path(shortestPath)
        self.update_maze_widget_attributes(randomColor, shortestPath)
        self.set_save_interval(queue_size)
        self.dump_buffer_and_compute_maze(maze)
        self.maze_widget.total_frames += 1
        self.print_infos()

    def set_shortest_path(self, shortestPath):
        """Set the shortest path if it exists."""
        if shortestPath:
            self.shortestPath = shortestPath

    def update_maze_widget_attributes(self, randomColor, shortestPath):
        """Update the attributes of the maze widget."""
        self.maze_widget.BFS = self.BFS
        self.maze_widget.shortest_path = shortestPath
        self.maze_widget.random_color = randomColor

    def set_save_interval(self, queue_size):
        """Set the save interval based on the maze size and BFS queue size."""
        maze_size = len(self.maze) * len(self.maze[0])
        self.maze_widget.save_interval = maze_size // 100

        if self.BFS and queue_size > 0 and not self.maze_widget.shortest_path:
            buffer_length = len(self.maze_widget.buffer)
            self.maze_widget.save_interval = queue_size

        # Ensure the save interval is at least half the buffer size
        if (
            self.maze_widget.save_interval > self.maze_widget.buffer_size
            or self.maze_widget.save_interval > len(self.maze_widget.buffer)
        ):
            self.maze_widget.save_interval = self.maze_widget.buffer_size
        # Ensure the save interval is at least 1
        if self.maze_widget.save_interval == 0:
            self.maze_widget.save_interval = 1

    def dump_buffer_and_compute_maze(self, maze):
        """Dump the buffer if it's too large, and compute the maze at regular intervals."""
        if self.buffer_iterator % self.maze_widget.save_interval == 0 or self.DFS:
            self.maze_widget.compute(maze)
            self.buffer_iterator = 0

        self.buffer_iterator += 1

    def run_generation(self):
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])
        self.maze_widget.needs_update = False

        self.BFS = False
        self.DFS = False
        self.shortestPath = []
        self.maze_widget.total_frames = 0
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

    def dump_buffer(self):
        self.maze_widget.dump_buffer()

    def run_place_start_and_goal(self):
        sizeX = len(self.maze)
        sizeY = len(self.maze[0])
        self.maze_widget.needs_update = False
        self.maze_widget.total_frames = 0
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

        self.screen.refresh()

    def run_bfs(self):
        # Run the BFS algorithm
        clear_maze(self.maze)
        self.maze_widget.total_frames = 0
        self.BFS = True
        self.DFS = False
        self.shortestPath = []
        self.maze_widget.needs_update = False
        self.update_maze(self.maze)

        BFS(self.maze, maze_effect=self, start=self.start)

        self.shortestPath = compute_shortest_path(
            self.maze, self.goal, maze_effect=self
        )

        self.update_maze(self.maze)
        self.maze_widget.compute(self.maze)
        self.maze_widget.update_thread()

    def run_dfs(self):
        clear_maze(self.maze)
        self.maze_widget.total_frames = 0
        self.DFS = True
        self.BFS = False
        self.shortestPath = []
        self.update_maze(self.maze)
        self.maze_widget.needs_update = False

        # Run the DFS algorithm
        DFS(self.maze, self, self.start)
        self.update_maze(self.maze)
        self.maze_widget.compute(self.maze)
        self.maze_widget.update_thread()

        while (
            not self.maze_widget.thread is None and self.maze_widget.thread.is_alive()
        ):
            time.sleep(1 / self.maze_widget.max_fps)

        self.screen.clear()
        self.screen.refresh()

    def quit(self):
        raise StopApplication("User chose to quit")
