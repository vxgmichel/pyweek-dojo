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

    filename = {1: "player_1",
                2: "player_2",}

    def get_image(self):
        filename = self.filename[self.model.id]
        return self.resource.image.getfile(filename)

    def get_rect(self):
        return self.model.rect


# Dojo view
class DojoView(BaseView):
    """Dojo view for the main game state."""
    bgd_image = "image/room"
    bgd_color = "darkgrey"
    
    sprite_class_dct = {PlayerModel: PlayerSprite,
                        DojoModel: DojoSprite,}

    def get_screen(self):
        return Surface(self.model.size)


