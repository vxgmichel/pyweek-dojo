"""Contain the view for the main game state."""

# Imports
import pygame as pg
from collections import defaultdict
from pygame import Rect, Surface, transform, draw, Color
from mvctools import BaseView, AutoSprite, xytuple
from dojo.model import DojoModel, PlayerModel, RectModel
from dojo.common import Dir

# Dojo sprite
class DojoSprite(AutoSprite):
    """Dojo sprite"""

# Player sprite
class PlayerSprite(AutoSprite):
    """Dojo sprite"""

    player_dct = {1: "player_1",
                  2: "player_2",}

    ko_dct = {1: "ko_1",
              2: "ko_2",}

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
        # Animation
        timer = self.model.timer
        filename = self.player_dct[self.model.id]
        resource = self.resource.image.get(filename)
        self.resource_dct = self.generate_animation_dct(resource, timer)
        # KO
        filename = self.ko_dct[self.model.id]
        self.ko = self.resource.image.get(filename)

    def get_image(self):
        if self.model.ko:
            return self.ko
        return self.get_animation().get()

    def get_rect(self):
        return self.model.rect

class RectSprite(AutoSprite):

    def get_rect(self):
        return self.model.rect

    def get_layer(self):
        return 9**9

    def get_image(self):
        img = Surface(self.rect.size).convert_alpha()
        img.fill((0,0,0,0), special_flags=pg.BLEND_RGBA_MULT)
        draw.rect(img, self.model.color, img.get_rect(), 1)
        img.fill((255,255,255,128), special_flags=pg.BLEND_RGBA_MULT)
        return img



# Dojo view
class DojoView(BaseView):
    """Dojo view for the main game state."""
    bgd_image = "image/room"
    bgd_color = "darkgrey"
    
    sprite_class_dct = {PlayerModel: PlayerSprite,
                        DojoModel: DojoSprite,
                        RectModel: RectSprite}

    def get_screen(self):
        return Surface(self.model.size)


