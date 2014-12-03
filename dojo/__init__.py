"""Dojo game package for the Pyweek 19."""

# Imports
import os, pygame, dojo
from mvctools import BaseControl, BaseState
from dojo.model import DojoModel
from dojo.view import DojoView
from dojo.controller import DojoController

# Get root
def relative(path):
    """Relative path to find resources."""
    return os.path.join(dojo.__path__[0], os.pardir, path)

# Create the main game state
class DojoState(BaseState):
    """Dojo main game state."""

    controller_class = DojoController
    model_class = DojoModel
    view_class = DojoView

# Create the main control
class Dojo(BaseControl):
    """
    Dojo: a minimalistic versus fighting game
    -----------------------------------------
    In one dojo, with one life, so one hit causes one win.
    The gameplay is based on the fact that you can grab the walls
    and ceiling of the room to jump on your opponent.
    """

    window_title = "Dojo"
    first_state = DojoState
    resource_dir = relative("resource")
    version = "1.3.0"

    def pre_run(self) :
        """Hide the mouse"""
        super(Dojo, self).pre_run()
        pygame.mouse.set_visible(False)

# Main function
def main():
    dojo = Dojo()
    # Uncomment to display all settings in help
    # dojo.settings.arg_lst = None
    dojo.main()
