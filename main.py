from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.exceptions import StopApplication
import os


from maze_input_frame import MazeInputFrame
from solver_menu_frame import SolverMenuFrame
from maze_solver_scene import MazeSolverScene


# Function to get terminal size
def get_terminal_size():
    return os.get_terminal_size()


# Function to check if the maze fits within the terminal
def check_if_maze_fits(maze_width, maze_height):
    # Get the terminal size
    terminal_width, terminal_height = get_terminal_size()

    # Leave some space for borders and other UI elements
    available_width = terminal_width // 2
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

    while not fits:
        terminal = get_terminal_size()
        prompt = f"Please zoom out the terminal to fit the maze (current size: {terminal.columns}x{terminal.lines})."
        prompt2 = f"Maze size: {maze_width}x{maze_height}"
        prompt3 = f"Available size: {available_width}x{available_height}"
        instructions = "Use Ctrl + - to zoom out, Ctrl + + to zoom in."

        # Calculate the position to center the box
        box_width = max(len(prompt), len(prompt2), len(prompt3), len(instructions)) + 4
        box_height = 7
        start_x = (terminal.columns - box_width) // 2
        start_y = (terminal.lines - box_height) // 2

        # Draw the box
        for y in range(start_y, start_y + box_height):
            for x in range(start_x, start_x + box_width):
                if y in (start_y, start_y + box_height - 1) or x in (
                    start_x,
                    start_x + box_width - 1,
                ):
                    screen.print_at("█", x, y)
                else:
                    screen.print_at(" ", x, y)

        # Print the prompts inside the box
        screen.print_at(prompt.center(box_width - 2), start_x + 1, start_y + 1)
        screen.print_at(prompt2.center(box_width - 2), start_x + 1, start_y + 2)
        screen.print_at(prompt3.center(box_width - 2), start_x + 1, start_y + 3)
        screen.print_at(instructions.center(box_width - 2), start_x + 1, start_y + 5)

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
    scenes = [Scene(effects, -1)]
    scene = None
    # Play the solver menu, stop on resize and restart on resize

    while True:
        try:
            screen.play(
                scenes,
                stop_on_resize=True,
                start_scene=scene,
                allow_int=True,
            )
            quit()
        except ResizeScreenError as e:
            """ ResizeScreenError is raised when the screen is resized """
            """ Resize the screen and prompt for zoom """
            # Common settings for screen
            screen.clear()
            screen.refresh()

            scene = e.scene
            screen.set_scenes([scene])
            prompt_for_zoom(screen, sizeX, sizeY)

            screen.clear()
            screen.refresh()
            screen.force_update()

            continue


if __name__ == "__main__":
    try:
        Screen.wrapper(Main)
        quit()
    except KeyboardInterrupt:
        # Clean threads still running
        os._exit(0)
