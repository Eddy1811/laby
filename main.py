import os
import threading
from time import sleep
from display import printLabyrinth
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, TextBox, Layout, Label, Text, Button, Divider
from asciimatics.exceptions import StopApplication
from asciimatics.screen import Screen
from generation import (
    generateLabyrinth,
    mergeMazeGeneration,
    clearLabyrinth,
    addRandomStartAndGoal,
)
from display import printLabyrinth
from solver import BFS, DFS


class MazeInputFrame(Frame):
    def __init__(self, screen, input_data):
        super(MazeInputFrame, self).__init__(
            screen,
            screen.height // 2,
            screen.width // 2,
            has_border=True,
            name="Maze Input Form",
        )

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
    def __init__(self, screen, lab, start):
        super(SolverMenuFrame, self).__init__(
            screen, screen.height, screen.width, has_border=False
        )

        self.lab = lab
        self.start = start
        self.goal = (len(lab) - 1, len(lab[0]) - 1)  # Goal position

        # Layout for menu options
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        self.message_label = Label("Select the algorithm to run:")
        layout.add_widget(self.message_label)

        # Buttons to select BFS and DFS
        layout.add_widget(Button("Run BFS", self.run_bfs))
        layout.add_widget(Button("Run DFS", self.run_dfs))
        layout.add_widget(Button("Quit", self.quit))
        printLabyrinth(screen, lab)
        self.fix()

    def run_bfs(self):
        # Run the BFS algorithm
        BFS(self.screen, self.lab, self.start)
        self.screen.force_update()
        sleep(2)  # Wait a moment to let user see the output
        clearLabyrinth(self.lab)

    def run_dfs(self):
        # Run the DFS algorithm
        DFS(self.screen, self.lab, self.start)
        sleep(2)  # Wait a moment to let user see the output
        self.screen.force_update()
        clearLabyrinth(self.lab)

    def quit(self):
        raise StopApplication("User chose to quit")


def Main(screen):
    # External dictionary to store width and height
    user_input = {"width": None, "height": None}

    # Create and play scene for input
    scenes = [Scene([MazeInputFrame(screen, user_input)], -1)]
    screen.play(scenes, stop_on_resize=True)

    # Retrieve width and height after scene has finished
    sizeX = user_input["width"]
    sizeY = user_input["height"]

    if sizeX is None or sizeY is None:
        raise ValueError("Maze dimensions were not entered correctly!")

    # Common settings for screen
    screen.clear()
    screen.refresh()
    # screen.set_title("Maze Solver")

    # Generate maze and start/end positions
    lab = generateLabyrinth(sizeX, sizeY)
    mergeMazeGeneration(screen, lab, sizeX, sizeY)
    clearLabyrinth(lab)
    [start, goal] = addRandomStartAndGoal(lab, sizeX, sizeY)
    printLabyrinth(screen, lab)
    sleep(3)
    # Create a frame to show BFS and DFS in parallel
    solver_frame = SolverMenuFrame(screen, lab, start)
    scene = Scene([solver_frame], -1)

    # Play the solver menu
    screen.play([scene], stop_on_resize=True)

    # After finishing with the menu
    screen.clear()
    screen.refresh()


if __name__ == "__main__":
    Screen.wrapper(Main)
