from asciimatics.scene import Scene
from asciimatics.screen import Screen

from display import (
    MazeInputFrame,
    MazeSolverScene,
)


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

    # Generate maze and start/end positions

    # Clear the screen and display the solver menu
    scene = MazeSolverScene(screen, sizeX, sizeY)
    # Play the solver menu
    screen.play([scene], stop_on_resize=True)

    # After finishing with the menu
    # screen.clear()
    screen.refresh()


if __name__ == "__main__":
    Screen.wrapper(Main)
