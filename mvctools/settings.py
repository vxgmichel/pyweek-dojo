import pygame
from mvctools.common import xytuple, Color

class BaseSettings(object):
    def __init__(self, control):
        self.control = control
        # Directories
        self.font_dir = "font"
        self.image_dir = "image"
        self.sound_dir = "sound"
        # Debug
        self.debug_speed = 1.0
        self.debug_mode = False
        self.display_fps = False
        self.profile = False
        # Settings
        self._fps = 60
        self._width = 1280
        self._height = 720
        self._fullscreen = False

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return xytuple(self._width, self._height)

    @size.setter
    def size(self, value):
        if isinstance(value, basestring):
            value = value.lower().split('x')
            value = map(int, value)
        if any(self.size-value):
            self._width, self._height = value

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        if isinstance(value, basestring):
            value = int(value)
        self._fps = value

    @property
    def fullscreen(self):
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, basestring):
            if value.lower().startswith('full'):
                value = True
            elif value.lower().startswith('window'):
                value = False
        if not isinstance(value, bool):
            raise ValueError
        if value != self.fullscreen:
            self._fullscreen = value

    # Fullscreen alias
    mode = fullscreen

    def string_setting(self, name, default=None):
        if name in ["size"]:
            return "x".join(map(str, self.size))
        if name in ["fullscreen", "mode"]:
            return {True: "fullscreen", False: "windowed"}.get(self.mode)
        if name in ["fps"]:
            return str(self.fps)
        if name in ["width"]:
            return str(self.width)
        if name in ["height"]:
            return str(self.height)
        return default
