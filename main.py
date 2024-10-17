from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import os

from display import MazeInputFrame, MazeSolverScene, SolverMenuFrame


# Function to get terminal size
def get_terminal_size():
    return os.get_terminal_size()


# Function to check if the maze fits within the terminal
def check_if_maze_fits(maze_width, maze_height):
    # Get the terminal size
    terminal_width, terminal_height = get_terminal_size()

    # Leave some space for borders and other UI elements
    available_width = terminal_width - 4
    available_height = terminal_height - 15

    # Check if the maze fits
    if maze_width > available_width or maze_height > available_height:
        return False, available_width, available_height
    return True, available_width, available_height


# Function to give zoom instructions based on the terminal
def prompt_for_zoom(screen, maze_width, maze_height):
    # Check if the maze fits within the terminal
    fits, available_width, available_height = check_if_maze_fits(
        maze_width, maze_height
    )

    # Adjust the terminal size
    # Zoom in/out the terminal based on the maze size
    while not fits:
        terminal = get_terminal_size()
        prompt = f"Please zoom out the terminal to fit the maze (current size: {terminal.columns}x{terminal.lines})."
        prompt2 = f"\nMaze size: {maze_width}x{maze_height}"
        prompt3 = f"\nAvailable size: {available_width}x{available_height}"
        screen.print_at(prompt, 10, 10)
        screen.print_at(prompt2, 10, 12)
        screen.print_at(prompt3, 10, 14)

        # Wait for user input (Ctrl + - to zoom out, Ctrl + + to zoom in)
        screen.refresh()
        while True:
            if screen.has_resized():
                screen.clear()
                screen.refresh()
                break
        fits, available_width, available_height = check_if_maze_fits(
            maze_width, maze_height
        )


def Main(screen):
    # External dictionary to store width and height
    user_input = {"width": None, "height": None}

    # Create and play scene for input
    scenes = [Scene([MazeInputFrame(screen, user_input)], -1)]
    screen.play(scenes, stop_on_resize=True)

    # Retrieve width and height after scene has finished
    sizeX = user_input["width"] or 35
    sizeY = user_input["height"] or 35
    sizeX = int(int(sizeX) * 1.2)
    sizeY = int(sizeY)

    # Common settings for screen
    screen.clear()
    screen.refresh()

    # Prompt the user to adjust zoom if necessary
    prompt_for_zoom(screen, sizeX, sizeY)
    screen = Screen.open()
    # Validate the input
    if sizeX is None or sizeY is None:
        raise ValueError("Maze dimensions were not entered correctly!")

    # Generate maze and start/end positions
    effects = [SolverMenuFrame(screen, sizeX, sizeY)]

    # Clear the screen and display the solver menu
    scene = MazeSolverScene(screen, sizeX, sizeY, effects)
    # Play the solver menu, stop on resize and restart on resize

    while True:
        try:
            screen.play([scene], stop_on_resize=True)
        except ResizeScreenError as e:
            effect = scene.effects[0]
            screen.clear()
            effect.canvas.refresh()
            effect.layout.reset()
            effect.layout.fix(0, 0, screen.width, screen.height)
            effect.fix()
            screen = Screen.open()

            # scene.reset(e.scene, screen)
            screen.clear()
            screen.refresh()
            continue


if __name__ == "__main__":
    try:
        Screen.wrapper(Main)
    except KeyboardInterrupt:
        # Clean threads still running
        os._exit(0)
