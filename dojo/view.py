"""Contain the view for the main game state."""

# Imports
from pygame import Rect, Surface
from mvctools import BaseView, AutoSprite, xytuple
from dojo.model import DojoModel, PlayerModel

# Dojo sprite
class DojoSprite(AutoSprite):
    """Dojo sprite"""

class PlayerSprite(AutoSprite):
    """Dojo sprite"""

    filename = "ash"

    def get_image(self):
        return self.resource.image.getfile(self.filename)

    def get_rect(self):
        return self.model.rect


# Dojo view
class DojoView(BaseView):
    """Dojo view for the main game state."""
    bgd_color = "lightgrey"
    sprite_class_dct = {PlayerModel: PlayerSprite,
                        DojoModel: DojoSprite,}

    def get_screen(self):
        return Surface(self.model.size)


