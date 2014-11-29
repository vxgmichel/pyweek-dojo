"""Contain the view for the main game state."""

# Imports
import pygame as pg
from collections import defaultdict
from pygame import Rect, Surface, transform, draw, Color
from mvctools import BaseView, AutoSprite, xytuple
from mvctools.utils import TextSprite
from mvctools.utils.renderer import opacify
from mvctools.utils.camera import CameraView
from dojo.model import PlayerModel, RectModel, RoomModel
from dojo.common import Dir, DIR_TO_ATTR


# Settings for text sprites
class WhiteTextSprite(TextSprite):

    # Font settings
    font_name = "visitor2"
    font_size = 20
    antialias = False
    color = "white"
    opacity = 0.3
    margin = -3


# Room sprite
class RoomSprite(AutoSprite):
    """Room background sprite."""

    string_dct = {1: ("P1\n-RDFG-\nJUMP-X", "left"),
                  2: ("P2\nARROWS\nJUMP-P", "right"),}
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


def opacify_ip(surface, opacity):
    if opacity < 1:
        color = 255, 255, 255, int(255 * opacity)
        surface.fill(color, special_flags=pg.BLEND_RGBA_MULT)


# Aura sprite
class AuraSprite(AutoSprite):
    """Aura sprite."""

    opacity = 1

    perp_name = "aura/aura_perp"
    diag_name = "aura/aura_diag"

    perp_dir = [Dir.UP, Dir.LEFT, Dir.DOWN, Dir.RIGHT]
    diag_dir = [Dir.UPRIGHT, Dir.UPLEFT, Dir.DOWNLEFT, Dir.DOWNRIGHT]

    def init(self):
        """Initialize the resources."""
        self.resource_dct = self.generate_resource_dct()
        self.layer = self.parent.layer + 10

    def get_image(self):
        if self.model.fixed and not self.model.ko:
            return self.resource_dct[self.model.current_dir]

    def get_rect(self):
        attr = DIR_TO_ATTR[self.model.current_dir]
        center = getattr(self.model.rect, attr)
        return self.image.get_rect(center=center)

    def generate_resource_dct(self):
        """Genrerate animations with rotations and flipping."""
        dct = {Dir.NONE: None}
        # Raw
        diag_image = self.resource.image.get(self.diag_name)
        perp_image = self.resource.image.get(self.perp_name)
        # Rotate
        for r in range(4):
            dct[self.perp_dir[r]] = transform.rotate(perp_image, 90*r)
            dct[self.diag_dir[r]] = transform.rotate(diag_image, 90*r)
        # Opacify
        for image in dct.values():
            if image:
                opacify_ip(image, self.opacity)
        # Return
        return dct

# Flash function
def flash(image, black):
    result = image.copy()
    delta = 64 if black else 32
    color = (delta, delta, delta*2, 0)
    flag = pg.BLEND_RGBA_SUB if black else pg.BLEND_RGBA_ADD
    result.fill(color, special_flags=flag)
    return result

# Player sprite
class PlayerSprite(AutoSprite):
    """Player sprite. Handle player animation."""

    # Filenames

    player_dct = {1: "player_1",
                  2: "player_2",}

    ko_dct = {1: "ko/ko_player_1",
              2: "ko/ko_player_2",}

    # Direction to ressource

    fixed_convert_dct = {Dir.NONE:  (False, False, 0),
                         Dir.UP:    (False, True,  0),
                         Dir.DOWN:  (False, False, 0),
                         Dir.LEFT:  (False, False, 3),
                         Dir.RIGHT: (True,  False, 1),}

    perp_names = {1: "jumping/perp_player_1",
                  2: "jumping/perp_player_2",}
    diag_names = {1: "jumping/diag_player_1",
                  2: "jumping/diag_player_2",}

    perp_dir = [Dir.UP, Dir.LEFT, Dir.DOWN, Dir.RIGHT]
    diag_dir = [Dir.UPRIGHT, Dir.UPLEFT, Dir.DOWNLEFT, Dir.DOWNRIGHT]

    def init(self):
        """Initialize the resources."""
        # Animation
        self.layer = 10
        timer = self.model.timer
        filename = self.player_dct[self.model.id]
        resource = self.resource.image.get(filename)
        self.resource_dct = self.generate_animation_dct(resource, timer)
        # Jumping
        self.jumping_dct = self.generate_jumping_dct(self.model.id)
        # KO
        filename = self.ko_dct[self.model.id]
        self.ko = self.resource.image.get(filename)
        # Aura
        self.aura = AuraSprite(self)

    def get_image(self):
        """Return the current image to use."""
        # KO
        if self.model.ko:
            return self.ko
        # Blinking
        if round(self.model.blinking_timer.get(normalized=True)):
            return Surface((0,0))
        # Fixed
        if self.model.fixed:
            arg = self.fixed_convert_dct[self.model.pos]
            arg += (self.model.loading,)
            return self.resource_dct[arg].get()
        # Moving
        return self.jumping_dct.get(self.model.current_dir, self.image)

    def get_rect(self):
        """Return the current rect to use."""
        return self.model.rect

    def get_layer(self):
        """Return the current layer."""
        return not self.model.fixed

    def generate_jumping_dct(self, pid):
        """Genrerate animations with rotations and flipping."""
        dct = {}
        # Raw
        diag_image = self.resource.image.get(self.diag_names[pid])
        perp_image = self.resource.image.get(self.perp_names[pid])
        # Rotate
        for r in (0,3):
            dct[self.perp_dir[r]] = transform.rotate(perp_image, r*90)
            dct[self.diag_dir[r]] = transform.rotate(diag_image, r*90)
        if pid == 2:
            dct[self.perp_dir[3]] = transform.flip(dct[self.perp_dir[3]], 0, 1)
        dct[self.diag_dir[1]] = transform.flip(dct[self.diag_dir[0]], 1, 0)
        dct[self.diag_dir[2]] = transform.flip(dct[self.diag_dir[3]], 1, 0)
        dct[self.perp_dir[1]] = transform.flip(dct[self.perp_dir[3]], 1, 0)
        dct[self.perp_dir[2]] = transform.rotate(perp_image, 180)
        # Return
        return dct

    def generate_animation_dct(self, resource, timer):
        """Genrerate animations with rotations and flipping."""
        dct = {}
        for h in range(2):
            for v in range(2):
                for r in range(4):
                    lst = [transform.rotate(transform.flip(img, h, v), 90*r)
                               for img in resource]
                    for l in range(2):
                        if l:
                            lst = [flash(image, i/2) for i, image in enumerate(lst)]
                        dct[h,v,r,l] = self.build_animation(lst, timer=timer)
        return dct


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
class StaticDojoView(BaseView):
    """Dojo view without the camera move."""

    bgd_image = "image/room"
    bgd_color = "darkgrey"

    sprite_class_dct = {PlayerModel: PlayerSprite,
                        RoomModel: RoomSprite,
                        RectModel: RectSprite}

    def get_screen(self):
        """Create game screen."""
        return Surface(self.model.size)


# Dojo camera view
class DojoView(CameraView):
    """Dojo view for the game state."""

    view_cls = StaticDojoView
    transparent = False
    fixed_size = 640, 360


