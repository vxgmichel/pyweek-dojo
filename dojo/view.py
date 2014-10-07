"""Contain the view for the main game state."""

# Imports
from pygame import Rect
from mvctools import BaseView, AutoSprite, xytuple
from dojo.model import DojoModel, PlayerModel

# Dojo sprite
class DojoSprite(AutoSprite):
    """Dojo sprite"""

class PlayerSprite(AutoSprite):
    """Dojo sprite"""

    filename = "ash"

    def get_image(self):
        size = self.convert_tuple(self.model.size)
        return self.resource.image.getfile(self.filename, size)

    def get_rect(self):
        print self.model.rect
        return self.convert_rect(self.model.rect)

    def convert_rect(self, rect):
        return self.parent.convert_rect(rect)

    def convert_tuple(self, xy):
        return self.parent.convert_tuple(xy)


# Dojo view
class DojoView(BaseView):
    """Dojo view for the main game state."""
    bgd_color = "lightgrey"
    sprite_class_dct = {PlayerModel: PlayerSprite,
                        DojoModel: DojoSprite,}

    @property
    def ratio(self):
        return self.settings.size.map(float) / self.model.size

    def convert_tuple(self, xy):
        return (self.ratio * xy).map(int)

    def convert_rect(self, rect):
        pos = self.convert_tuple(rect.topleft)
        size = self.convert_tuple(rect.size)
        return Rect(pos, size)


