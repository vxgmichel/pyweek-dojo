"""Provide the view for the main game state."""

# Pygame imports
import pygame as pg
from pygame import Surface, transform, draw

# MVC tools imports
from mvctools import BaseView, AutoSprite, Dir, xytuple
from mvctools.utils import TextSprite, MenuSprite
from mvctools.utils import CameraSprite

# Dojo imports
from dojo.model import PlayerModel, RectModel, RoomModel, TitleMenuModel
from dojo.model import SettingsMenuModel
from dojo.common import opacify_ip, flash


# Settings for text sprites
class WhiteTextSprite(TextSprite):
    """Apply new settings for the text sprites."""

    # Font settings
    font_name = "visitor2"
    antialias = False
    color = "white"
    opacity = 0.3


# Room sprite
class RoomSprite(AutoSprite):
    """Room background sprite."""

    string_dct = {0: ("CONTROLLER\nSTICK  \nJUMP-A \nRESET-Y", "center"),
                  1: ("P1\n-RDFG-\nJUMP-X\n/SPACE", "left"),
                  2: ("P2\nARROWS\nJUMP-P\n/ENTER", "right")}

    def init(self):
        """Initialize the sprite."""
        TitleSprite(self)
        for player, (text, alignment) in self.string_dct.items():
            if self.model.display_scores and player:
                ScoreSprite(self, player=player)
            if self.model.display_controls:
                ControlSprite(self, player=player,
                              text=text,
                              alignment=alignment)
        if self.model.display_scores:
            ResetSprite(self)


# Title sprite
class TitleSprite(WhiteTextSprite):
    """Title line."""

    # Settings
    relative_pos = 0.505, 0.25
    font_size = 24

    @property
    def pos(self):
        """Position for the center of the title."""
        size = xytuple(*self.model.rect.bottomright)
        return (size * self.relative_pos).map(round)

    @property
    def text(self):
        """Text from the model."""
        return self.model.text


# Reset sprite
class ResetSprite(WhiteTextSprite):
    """Reset line."""

    # Settings
    font_size = 12
    relative_pos = 0.503, 0.5
    alignment = "center"
    interline = -2
    text_dict = {(False, None): "JUMP!\n ",
                 (True, None): "REMATCH\n-U-",
                 (True, 1): "PLAYER 1\nWINS!",
                 (True, 2): "PLAYER 2\nWINS!"}

    @property
    def text(self):
        """Text from the model."""
        key = self.model.gameover, self.model.winner
        return self.text_dict.get(key, "")

    @property
    def pos(self):
        """Position for the center of the reset text."""
        size = xytuple(*self.model.rect.bottomright)
        return (size * self.relative_pos).map(round)


# Score sprite
class ScoreSprite(WhiteTextSprite):
    """Score sprite"""

    # Settings
    font_size = 24
    pos_dct = {1: (0.23, 0.35),
               2: (0.79, 0.35)}

    @property
    def pos(self):
        """Position for the center of the score panels."""
        size = xytuple(*self.model.rect.bottomright)
        return (size * self.pos_dct[self.player]).map(round)

    @property
    def text(self):
        """Text from the model."""
        return "{:02}".format(self.model.score_dct[self.player])


# Control sprite
class ControlSprite(WhiteTextSprite):
    """Control lines."""

    # Settings
    font_size = 12
    interline = -3
    pos_dct = {1: (0.23, 0.38),
               2: (0.78, 0.38),
               0: (0.5, 0.7)}

    @property
    def pos(self):
        """Position for the center of the control panels."""
        size = xytuple(*self.model.rect.bottomright)
        return (size * self.pos_dct[self.player]).map(round)


# Title menu sprite
class DojoMenuSprite(MenuSprite):

    # Entries
    font_sizes = 12, 12
    font_name = "visitor2"
    colors = "white", "black"
    opacity = 0.3
    alignment = "left"
    interlines = 20, 0

    # Position
    reference = "center"
    position_ratio = 0.5, 0.59

    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)


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
        """Get corresponding image if the player stand up."""
        if self.model.fixed and not self.model.ko and not self.model.colliding:
            return self.resource_dct[self.model.current_dir]

    def get_rect(self):
        """Get the corresponding rectangle."""
        attr = Dir.DIR_TO_ATTR[self.model.current_dir]
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


# Player sprite
class PlayerSprite(AutoSprite):
    """Player sprite. Handle player animation."""

    # Filenames

    player_dct = {1: "player_1",
                  2: "player_2"}

    ko_dct = {1: "ko/ko_player_1",
              2: "ko/ko_player_2"}

    # Direction to ressource

    fixed_convert_dct = {Dir.NONE:  (False, False, 0),
                         Dir.UP:    (False, True,  0),
                         Dir.DOWN:  (False, False, 0),
                         Dir.LEFT:  (False, False, 3),
                         Dir.RIGHT: (True,  False, 1)}

    perp_names = {1: "jumping/perp_player_1",
                  2: "jumping/perp_player_2"}
    diag_names = {1: "jumping/diag_player_1",
                  2: "jumping/diag_player_2"}

    # Directions

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
        # Blinking
        value = self.model.blinking_timer.get(normalized=True)
        self.visible = not round(value)
        # KO
        if self.model.ko:
            return self.ko
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
        for r in (0, 3):
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
                            lst = [flash(image, not i/2)
                                   for i, image in enumerate(lst)]
                        key = h, v, r, l
                        dct[key] = self.build_animation(lst, timer=timer)
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
        img.fill((0, 0, 0, 0), special_flags=pg.BLEND_RGBA_MULT)
        draw.rect(img, self.model.color, img.get_rect(), 1)
        img.fill((255, 255, 255, 128), special_flags=pg.BLEND_RGBA_MULT)
        return img


# Dojo view
class StaticDojoView(BaseView):
    """Dojo view without the camera move."""

    # Settings
    bgd_image = "image/room"
    transparent = False

    sprite_class_dct = {PlayerModel: PlayerSprite,
                        RoomModel: RoomSprite,
                        RectModel: RectSprite,
                        TitleMenuModel: DojoMenuSprite,
                        SettingsMenuModel: DojoMenuSprite}

    @property
    def size(self):
        """Create game screen."""
        return self.model.size


# Dojo camera view
class DojoView(BaseView):
    """Dojo view for the game state."""

    # Settings
    subview = StaticDojoView
    transparent = False
    size = 640, 360

    def init(self):
        """Create the camera sprite."""
        self.camera = CameraSprite(self, self.subview)
