"""Dojo game package for the Pyweek 19."""

# Imports
import os, pygame, dojo
from mvctools import BaseControl
from dojo.state import DemoState

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
    first_state = DemoState
    resource_dir = "resource"
    version = "1.3.1"

    def pre_run(self) :
        """Hide the mouse"""
        super(Dojo, self).pre_run()
        pygame.mouse.set_visible(False)


# Main function
def main():
    dojo = Dojo()
    # Uncomment to display debug settings in help
    # dojo.settings.arg_lst = None
    dojo.main()
