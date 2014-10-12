"""Contain the view for the main game state."""

# Imports
import pygame as pg
from collections import defaultdict
from pygame import Rect, Surface, transform, draw, Color
from mvctools import BaseView, AutoSprite, xytuple
from mvctools.utils import RendererSprite
from dojo.model import DojoModel, PlayerModel, RectModel
from dojo.common import Dir

# Line sprite
class LineSprite(RendererSprite):
    """Line of text."""

    # Font settings
    font_folder = "font"
    font_name = "visitor2"
    font_size = 20
    font_color = "white"
    font_opacity = 0.3
    margin = 3

    def get_center(self):
        """Return the enter of the sprite."""
        return 0,0

    def init(self, text, left=True, link=False):
        """Initialize the sprite."""
        RendererSprite.init(self)
        self.image = self.renderer(text)
        if link and left:
            self.rect = self.image.get_rect(topleft=self.parent.rect.bottomleft)
            self.rect.top -= self.margin
        elif link:
            self.rect = self.image.get_rect(topright=self.parent.rect.bottomright)
            self.rect.top -= self.margin
        else:
            self.rect = self.image.get_rect(center=self.get_center())


# Dojo sprite
class MultilineSprite(LineSprite):
    """Several lines of text."""

    def init(self, text, left=True, link=False):
        """Initialize the sprite."""
        if isinstance(text, basestring):
            text = text.split('\n')
        if not len(text):
            return
        LineSprite.init(self, text[0], left=left, link=link)
        text = text[1:]
        if not len(text):
            return
        type(self)(self, text, left=left, link=True)


# Dojo sprite
class DojoSprite(MultilineSprite):
    """Title sprite."""

    string_dct = {1: ("P1\n-WASD-\nTABKEY", True),
                  2: ("P2\nARROWS\nRSHIFT", False),}

    def init(self):
        """Initialize the sprite."""
        MultilineSprite.init(self, self.model.text)
        for key, (string, left) in self.string_dct.items():
            ControlSprite(self, string, left=left, player=key)
        ResetSprite(self, "RESET:R")

    def get_center(self):
        """Return the enter of the sprite."""
        center = xytuple(*self.model.rect.center)
        return center * (1, 0.6)


# Reset sprite
class ResetSprite(MultilineSprite):
    """Reset line."""
    
    font_size = 12
    pos = 0.5, 0.42
    
    def init(self, text, player=None, left=True, link=False):
        """Initialize the sprite."""
        self.player = player
        MultilineSprite.init(self, text, left, link)

    def get_center(self):
        """Return the enter of the sprite."""
        return xytuple(*self.model.rect.bottomright) * self.pos


# Control sprite
class ControlSprite(MultilineSprite):
    """Control sprite"""
    font_size = 12

    pos_dct = {1: (0.2, 0.6),
               2: (0.8, 0.6)}
    
    def init(self, text, player=None, left=True, link=False):
        self.player = player
        MultilineSprite.init(self, text, left, link)

    def get_center(self):
        size = xytuple(*self.model.rect.bottomright)
        return size * self.pos_dct[self.player]


# Player sprite
class PlayerSprite(AutoSprite):
    """Player sprite. Handle player animation."""

    # Filenames

    player_dct = {1: "player_1",
                  2: "player_2",}

    ko_dct = {1: "ko_1",
              2: "ko_2",}

    # Direction to ressource

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

    def init(self):
        """Initialize the resources."""
        # Animation
        timer = self.model.timer
        filename = self.player_dct[self.model.id]
        resource = self.resource.image.get(filename)
        self.resource_dct = self.generate_animation_dct(resource, timer)
        # KO
        filename = self.ko_dct[self.model.id]
        self.ko = self.resource.image.get(filename)

    def get_image(self):
        """Return the current image to use."""
        if self.model.ko:
            return self.ko
        return self.get_animation().get()

    def get_rect(self):
        """Return the current rect to use."""
        return self.model.rect

    def generate_animation_dct(self, resource, timer):
        """Genrerate animations with rotations and flipping."""
        dct = {}
        for h in range(2):
            for v in range(2):
                for r in range(4):
                    lst = [transform.rotate(transform.flip(img, h, v), 90*r)
                           for img in resource]
                    dct[h,v,r] = self.build_animation(lst, timer=timer) 
        return dct

    def get_animation(self):
        """Get the right animation depending on the model."""
        if self.model.fixed:
            return self.resource_dct[self.fixed_convert_dct[self.model.pos]]
        speed = self.model.speed
        if abs(speed.x) > abs(speed.y):
            key = cmp(speed.x, 0), 0
        else:
            key = 0, cmp(speed.y, 0)
        return self.resource_dct[self.jump_convert_dct[key]]

# Rectangle sprite
class RectSprite(AutoSprite):
    """Rect sprite for debug purposes"""
    
    def get_rect(self):
        """Return the current rect to use."""
        return self.model.rect

    def get_layer(self):
        """Display rect on top."""
        return 9**9

    def get_image(self):
        """Draw the rectange on a transparent surface."""
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
        """Separate actual screen and view screen."""
        return Surface(self.model.size)


