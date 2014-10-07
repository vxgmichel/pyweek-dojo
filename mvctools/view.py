import pygame as pg
from math import ceil
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface, transform
from functools import partial
from mvctools.common import xytuple, cachedict, Color

AutoGroup = partial(LayeredDirty, _use_updates = True, _time_threshold = 1000)

class BaseView(object):
    
    bgd_image = None
    bgd_color = None
    sprite_class_dct = {}

    def __init__(self, state, model):
        # Attributes to higher instances
        self.state = state
        self.model = model
        self.control = self.state.control
        self.resource = self.control.resource
        self.settings = self.control.settings
        # View-related attributes
        self.sprite_dct = {}
        self.group = AutoGroup()
        self.screen = self.get_screen()
        self.background = self.get_background()
        self.first_update = True
        # Call user initialisation
        self.init()

    def init(self):
        pass

    def get_screen(self):
        return pg.display.get_surface()
    
    def get_background(self):
        image = self.resource.get(self.bgd_image) if self.bgd_image else None
        return self.scale_as_background(image, self.bgd_color)

    def _reload(self):
        self.__init__(self, self.model)

    def _update(self):
        # Handle first update
        self.group._use_update = not self.first_update
        self.first_update = False
        # Update, draw and display
        self.gen_sprites()
        self.group.update()
        dirty = self.group.draw(self.screen, self.background)
        self.update_screen(dirty)
        
    def update_screen(self, dirty):
        actual = pg.display.get_surface()
        if actual != self.screen:
            size = actual.get_size()
            self.resource.scale(self.screen, size, actual)
            self.update_dirty(dirty)
        pg.display.update(dirty)

    def update_dirty(self, dirty):
        actual = pg.display.get_surface()
        actual_size = xytuple(*actual.get_size())
        ratio = actual_size.map(float)/self.size
        for rect in dirty:
            topleft = (ratio * rect.topleft).map(int)
            bottomright = (ratio * rect.bottomright).map(ceil)
            rect.topleft, rect.size = topleft, bottomright - topleft

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

    def scale_as_background(self, image=None, color=None):
        if not image and not color:
            return None
        color = Color(color)
        bgd = pg.Surface(self.size)
        bgd.fill(color)
        if image is not None:
            scaled = self.ressource.scale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd




