"""Dojo game package for the Pyweek 19."""


# Imports
import pygame
from mvctools import BaseControl, BaseSettings, default_setting
from dojo.state import DojoMainState


# Dojo settings
class DojoSettings(BaseSettings):
    """Custum setting class for Dojo."""

    # Display scoring
    arg_lst = list(BaseSettings.arg_lst)
    arg_lst.append("scoring")

    # Uncomment to display debug settings in help
    # arg_lst = None

    @default_setting(cast=int)
    def scoring(self):
        """Scoring to win the game"""
        return 20


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
    first_state = DojoMainState
    settings_class = DojoSettings
    resource_dir = "resource"
    version = "1.3.1"

    def pre_run(self):
        """Hide the mouse"""
        super(Dojo, self).pre_run()
        pygame.mouse.set_visible(False)


# Main function
def main():
    dojo = Dojo()

    dojo.main()
