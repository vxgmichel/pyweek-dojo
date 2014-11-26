import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface, transform
from functools import partial
import mvctools
from mvctools.common import xytuple, cachedict, Color

class AutoGroup(LayeredDirty):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("_time_threshold", 9e9)
        LayeredDirty.__init__(self, *args, **kwargs)

    def draw(self, screen, bgd=None):
        # Handle source_rect
        dct = dict((sprite, sprite._rect) for sprite in self if sprite.source_rect)
        for key, value in dct.items():
            key._rect = value.move(key.source_rect.topleft)
        # Call method
        dirty = LayeredDirty.draw(self, screen, bgd)
        # Restore rect
        for key, value in dct.items():
            key._rect = value
        # Force flag reset
        for sprite in self:
            sprite.dirty = 0 if sprite.dirty < 2 else 2
        # Return
        return [rect for rect in dirty if rect]

    def reset_update(self):
        self._use_update = False

    @property
    def is_drawn(self):
        return self._use_update

    @property
    def is_dirty(self):
        return any(sprite.dirty for sprite in self)

class BaseView(object):
    
    bgd_image = None
    bgd_color = None
    fixed_size = None
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

    def update_screen(self, force=False):
        if force or self.screen is None:
            self.screen = self.get_screen()
            self.background = self.get_background()
            self.group.reset_update()

    def reset_screen(self):
        self.screen = None

    def get_screen(self):
        size = self.fixed_size
        if size is None:
            data = self.parent.get_surface()
            if isinstance(data, Surface):
                return data
            size = data
        if not self.transparent:
            return Surface(size)
        return Surface(size, pg.SRCALPHA)
    
    def get_background(self):
        image = self.resource.get(self.bgd_image) if self.bgd_image else None
        return self.scale_as_background(image, self.bgd_color)

    def _reload(self):
        self.__init__(self, self.model)

    def _update(self):
        # Create screen
        self.update_screen()
        # Update
        self.update()
        self.gen_sprites()
        self.group.update()
        # Changes on a transparent background
        if self.transparent and self.group.is_drawn and self.group.is_dirty \
           or self.screen and self.size != self.screen.get_size():
            self.reset_screen()
        # Create screen
        self.update_screen()
        # Draw and display
        dirty = self.group.draw(self.screen, self.background)
        # Update dirty
        for sprite in self.group:
            if sprite.source_rect in dirty:
                dirty.remove(sprite.source_rect)
                try: dirty += sprite.dirty_rects
                except AttributeError: pass
        # Return
        return self.screen, dirty

    def update(self):
        pass
    
    def gen_sprites(self):
        for _, obj in self.model.get_model_dct():
            self.gen_sprite(obj)

    def gen_sprite(self, obj):
        if obj.key not in self.sprite_dct:
            cls = self.sprite_class_dct.get(obj.__class__, None)
            if cls:
                self.sprite_dct[obj.key] = cls(self, model=obj)

    @classmethod
    def register_sprite_class(cls, obj_cls, sprite_cls):
        cls.sprite_class_dct[obj_cls] = sprite_cls
        
    def get_models_at(self, pos):
        return [sprite.model
                for sprite in reversed(self.group.get_sprites_at(pos))]

    def get_sprite_from(self, model):
        self.gen_sprite(model)
        if model.key in self.sprite_dct: 
            return self.sprite_dct[model.key]
        gen_results = (sprite.view.get_sprite_from(model)
                           for sprite in self.group
                               if hasattr(sprite, "view"))
        gen_filtered = (result for result in gen_results if result)
        return next(gen_filtered, None)

    @property
    def size(self):
        if self.fixed_size is None:
            return self.screen.get_size()
        return self.fixed_size

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




