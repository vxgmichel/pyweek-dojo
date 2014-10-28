"""Contain the view for the main game state."""

# Imports
import pygame as pg
from collections import defaultdict
from pygame import Rect, Surface, transform, draw, Color
from mvctools import BaseView, AutoSprite, xytuple
from mvctools.utils import TextSprite
from dojo.model import DojoModel, PlayerModel, RectModel
from dojo.common import Dir


class WhiteTextSprite(TextSprite):

    # Font settings
    font_name = "visitor2"
    font_size = 20
    color = "white"
    opacity = 0.3
    margin = -3


# Dojo sprite
class DojoSprite(AutoSprite):
    """Dojo background sprite."""

    string_dct = {1: ("P1\n-RDFG-\nJUMP:X", "left"),
                  2: ("P2\nARROWS\nJUMP:P", "right"),}
    reset_string = "RESET:U"

    def init(self):
        """Initialize the sprite."""
        for player, (text, alignment) in self.string_dct.items():
            ScoreSprite(self, player=player)
            ControlSprite(self, player=player,
                          text=text,
                          alignment=alignment)
        ResetSprite(self, text=self.reset_string)
        TitleSprite(self)

# Title sprite
class TitleSprite(WhiteTextSprite):
    """Title line."""

    # Settings
    relative_pos = 0.5, 0.3

    @property
    def pos(self):
        size = xytuple(*self.model.rect.bottomright)
        return size * self.relative_pos

    @property
    def text(self):
        return self.model.text


# Reset sprite
class ResetSprite(WhiteTextSprite):
    """Reset line."""

    # Settings
    font_size = 12
    relative_pos = 0.5, 0.42

    @property
    def pos(self):
        size = xytuple(*self.model.rect.bottomright)
        return size * self.relative_pos

# Score sprite
class ScoreSprite(WhiteTextSprite):
    """Score sprite"""

    # Settings
    pos_dct = {1: (0.25, 0.4),
               2: (0.75, 0.4)}

    @property
    def pos(self):
        size = xytuple(*self.model.rect.bottomright)
        return size * self.pos_dct[self.player]

    @property
    def text(self):
        return "{:02}".format(self.model.score_dct[self.player])


# Control sprite
class ControlSprite(WhiteTextSprite):
    """Control lines."""

    # Settings
    font_size = 12
    pos_dct = {1: (0.25, 0.65),
               2: (0.75, 0.65)}

    @property
    def pos(self):
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


