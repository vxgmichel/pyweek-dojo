import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface, transform
from functools import partial
import mvctools
from mvctools.common import xytuple, cachedict, Color

AutoGroup = partial(LayeredDirty, _use_updates = True, _time_threshold = 1000)

class BaseView(object):
    
    bgd_image = None
    bgd_color = None
    sprite_class_dct = {}

    def __init__(self, parent, model):
        # Attributes to higher instances
        self.parent = parent
        self.model = model
        self.control = self.state.control
        self.resource = self.control.resource
        self.settings = self.control.settings
        # View-related attributes
        self.sprite_dct = {}
        self.group = AutoGroup()
        self.screen = None
        self.background = None
        self.first_update = True
        # Call user initialisation
        self.init()

    @property
    def state(self):
        return self.parent if self.root else self.parent.state

    @property
    def root(self):
        return isinstance(self.parent, mvctools.BaseState)

    def init(self):
        pass

    def create_screen(self):
        self.first_update = True
        self.screen = self.get_screen()
        self.background = self.get_background()

    def reset_screen(self):
        self.screen = None

    def get_screen(self):
        return self.parent.get_surface()
    
    def get_background(self):
        image = self.resource.get(self.bgd_image) if self.bgd_image else None
        return self.scale_as_background(image, self.bgd_color)

    def _reload(self):
        self.__init__(self, self.model)

    def _update(self):
        # Handle first update
        self.group._use_update = not self.first_update
        self.first_update = False
        # Update
        self.update()
        self.gen_sprites()
        self.group.update()
        # Changes on a transparent background
        if self.transparent and any(sprite.dirty for sprite in self.group):
            self.reset_screen()
        # No change on a transparent background
        elif self.transparent and self.screen:
            return self.screen, []
        # Create screen
        if self.screen is None:
            self.create_screen()
        # Draw and display
        dirty = self.group.draw(self.screen, self.background)
        # Force reset for dirtiness
        for sprite in self.group:
            if sprite.dirty == 1:
                sprite.dirty = 0
        # Return
        return self.screen, dirty

    def update(self):
        pass
    
    def gen_sprites(self):
        for key,obj in self.model.get_model_dct():
            if key not in self.sprite_dct:
                cls = self.get_sprite_class(obj)
                if cls:
                    self.sprite_dct[key] = cls(self, model=obj)

    def get_sprite_class(self, obj):
        return self.sprite_class_dct.get(obj.__class__, None)

    @classmethod
    def register_sprite_class(cls, obj_cls, sprite_cls):
        cls.sprite_class_dct[obj_cls] = sprite_cls
        
    def get_models_at(self, pos):
        return [sprite.model
                for sprite in reversed(self.group.get_sprites_at(pos))]

    @property
    def size(self):
        return self.screen.get_size()

    @property
    def transparent(self):        
        return not (self.bgd_image or self.bgd_color)

    def scale_as_background(self, image=None, color=None):
        if not image and not color:
            return None
        color = Color(color)
        bgd = pg.Surface(self.size)
        bgd.fill(color)
        if image is not None:
            scaled = self.resource.scale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd




