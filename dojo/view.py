"""Contain the view for the main game state."""

# Imports
from collections import defaultdict
from pygame import Rect, Surface, transform
from mvctools import BaseView, AutoSprite, xytuple
from dojo.model import DojoModel, PlayerModel
from dojo.common import Dir

# Dojo sprite
class DojoSprite(AutoSprite):
    """Dojo sprite"""

# Player sprite
class PlayerSprite(AutoSprite):
    """Dojo sprite"""

    filename = {1: "player_1",
                2: "player_2",}

    fixed_convert_dct = {Dir.NONE:  (False, False, 0),
                         Dir.UP:    (False, True,  0),
                         Dir.DOWN:  (False, False, 0),
                         Dir.LEFT:  (False, False, 3),
                         Dir.RIGHT: (True,  False, 1),}

    jump_convert_dct = {Dir.NONE:  (False, False, 0),
                        Dir.UP:    (False, True,  0),
                        Dir.DOWN:  (False, False, 0),
                        Dir.LEFT:  (False, False, 3),
                        Dir.RIGHT: (True,  False, 1),}

    def generate_animation_dct(self, resource, timer):
        dct = {}
        for h in range(2):
            for v in range(2):
                for r in range(4):
                    lst = [transform.rotate(transform.flip(img, h, v), 90*r)
                           for img in resource]
                    dct[h,v,r] = self.build_animation(lst, timer=timer) 
        return dct

    def get_animation(self):
        if self.model.fixed:
            return self.resource_dct[self.fixed_convert_dct[self.model.pos]]
        speed = self.model.speed
        if abs(speed.x) > abs(speed.y):
            key = cmp(speed.x, 0), 0
        else:
            key = 0, cmp(speed.y, 0)
        return self.resource_dct[self.jump_convert_dct[key]]
        

    def init(self):
        timer = self.model.timer
        filename = self.filename[self.model.id]
        resource = self.resource.image.get(filename)
        self.resource_dct = self.generate_animation_dct(resource, timer)


    @property
    def flip(self):
        if self.model.fixed:
            return self.pos
        return 

    def get_image(self):
        return self.get_animation().get()

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


