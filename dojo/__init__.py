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
    """Dojo game main class."""

    window_title = "Dojo"
    first_state = DojoState
    resource_dir = relative("resource")

    def pre_run(self) :
        """Hide the mouse"""
        super(Dojo, self).pre_run()
        pygame.mouse.set_visible(False)

# Main function
def main():
    dojo = Dojo()
    # Settings
    dojo.settings.fps = 60
    dojo.settings.size = 1280, 720
    dojo.settings.fullscreen = False
    # Debug
    dojo.settings.display_fps = False
    dojo.settings.profile = False
    dojo.settings.debug_speed = 1
    dojo.settings.debug_mode = False
    # Run
    dojo.run()
