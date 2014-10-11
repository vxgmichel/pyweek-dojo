"""Dojo game package for the Pyweek 19."""

# Imports
import os, pygame, dojo
from mvctools import BaseControl, BaseState
from mvctools.utils import BaseMenuController
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
    """Dojo game main class."""

    resource_dir = relative("resource")
    window_title = "Dojo"
    first_state = DojoState

    def pre_run(self) :
        """Hide the mouse"""
        pygame.mouse.set_visible(False)

# Main function
def main():
    dojo = Dojo()
    dojo.settings.fps = 60
    dojo.run()
