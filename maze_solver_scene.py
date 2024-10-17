from asciimatics.scene import Scene
from solver_menu_frame import SolverMenuFrame


# Scene that combine the maze and the solver menu to be displayed
#
class MazeSolverScene(Scene):
    def __init__(self, screen, sizeX, sizeY, effects=None):
        # Split the screen into two parts
        effects = effects or [SolverMenuFrame(screen, sizeX, sizeY)]

        super(MazeSolverScene, self).__init__(effects, -1, name="Maze Solver Scene")

    def create_effects(self, screen, sizeX, sizeY):
        return [SolverMenuFrame(screen, sizeX, sizeY)]
