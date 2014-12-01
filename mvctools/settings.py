"""Provide the base settings class."""

# Imports
import pygame
from mvctools import xytuple
from mvctools.property import setting, default_setting

# Fullscreen string conversion functions

def fullscreen_to_string(value):
    """Convert a boolean to a string."""
    return {True: 'windowed', False: 'fullscreen'}[value]

def fullscreen_from_string(string):
    """Convert a string to a boolean."""
    if string.lower() in ["fullscreen", "full", "1", "true"]:
        return True
    if string.lower() in ["window", "windowed", "0", "false"]:
        return False
    raise ValueError("not a valid string")


# Base settings class
class BaseSettings(object):
    """Base setting class"""

    def __init__(self, control):
        """Save the control."""
        self.control = control

    # Directories

    @default_setting(cast=str)
    def font_dir(self):
        return "font"

    @default_setting(cast=str)
    def image_dir(self):
        return "image"

    @default_setting(cast=str)
    def sound_dir(self):
        return "sound"

    # Debug

    @default_setting(cast=float)
    def debug_speed(self):
        return 1.0

    @default_setting(cast=bool)
    def debug_mode(self):
        return False

    @default_setting(cast=bool)
    def profile(self):
        return False

    # Settings

    @default_setting(cast=int)
    def fps(self):
        return 60

    @default_setting(cast=int)
    def width(self):
        return 1280

    @default_setting(cast=int)
    def height(self):
        return 720

    @default_setting(cast=bool, from_string=fullscreen_from_string,
                     to_string=fullscreen_to_string)
    def fullscreen(self):
        return False

    #: Alias of fullscreen
    mode = fullscreen

    @setting(from_string="x".split, to_string="{0[0]}x{0[1]}".format)
    def size(self):
        return xytuple(self._width, self._height)

    @size.setter
    def size(self, value):
        self.width, self.height = value

    # Setting to string

    def setting_to_string(self, name):
        return getattr(type(self), name).to_string(self)
