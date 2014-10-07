"""Dojo game package for the Pyweek 19."""

# Imports
import pygame
from mvctools import BaseControl, BaseState
from mvctools.utils import BaseMenuController
from dojo.model import DojoModel
from dojo.view import DojoView


# Create the main game state
class DojoState(BaseState):
    """Dojo main game state."""

    controller_class = BaseMenuController
    model_class = DojoModel
    view_class = DojoView

# Create the main control
class Dojo(BaseControl):
    """Dojo game main class."""

    ressource_dir = "resource"
    window_title = "Dojo"
    first_state = DojoState

    def pre_run(self) :
        """Hide the mouse"""
        pygame.mouse.set_visible(False)
