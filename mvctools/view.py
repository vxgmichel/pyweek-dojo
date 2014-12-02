
# Imports
import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface, transform
from functools import partial

# MVC tools imports
import mvctools
from mvctools.common import xytuple, cachedict, Color


# Base view class
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
        return self.build_background(image, self.bgd_color, self.size,
                                     self.transparent)

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
        if self.screen and self.size != self.screen.get_size():
            self.reset_screen()
        # Create screen
        self.update_screen()
        # Draw and display
        dirty = self.group.draw(self.screen, self.background)
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
        return self.bgd_color is None or Color(self.bgd_color)[3] != 255

    def build_background(self, image=None, color=None, size=None, transparent=False):
        # No background
        if image is None and color is None:
            return None
        # Get base
        if transparent:
             bgd = Surface(size, pg.SRCALPHA)
        else:
             bgd = Surface(size)
        # Fill with color
        if color is not None:
            color = Color(color)
            bgd.fill(color)
        # Blit image
        if image is not None:
            scaled = self.resource.scale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd


class PatchedLayeredDirty(LayeredDirty):

    def add_internal(self, sprite, layer=None):
        LayeredDirty.add_internal(self, sprite, layer)
        self.spritedict[sprite] = []

    def remove_internal(self, sprite):
        self._spritelist.remove(sprite)
        self.lostsprites.extend(self.spritedict[sprite])
        del self.spritedict[sprite]
        del self._spritelayers[sprite]

    def draw(self, surface, bgd=None):
        # speedups
        _orig_clip = surface.get_clip()
        _clip = self._clip
        if _clip is None:
            _clip = _orig_clip
        _surf = surface
        _sprites = self._spritelist
        _old_rects = self.spritedict
        _update = self.lostsprites
        _update_append = _update.append
        _ret = None
        _surf_blit = _surf.blit
        _surf_fill = _surf.fill
        _rect = Rect
        if bgd is not None:
            self._bgd = bgd
        _bgd = self._bgd
        _surf.set_clip(_clip)
        # 0. Prepare sprites
        for spr in _sprites:
            if not spr.dirty and spr.dirty_rects:
                spr.dirty = 1
            if spr.source_rect is None:
                actual_size = spr.rect.size
            else:
                actual_size = spr.source_rect.size
            actual_rect = _rect((0,0), actual_size)
            if spr.dirty_rects is None:
                spr.dirty_rects = [actual_rect]
            # Loop over dirty rects
            for k, area in enumerate(spr.dirty_rects):
                _union_rect = spr.dirty_rects[k] = area.clip(actual_rect)
        # 1. find dirty area on screen and put the rects into _update
        start_time = pg.time.get_ticks()
        if self._use_update:
            for spr in _sprites:
                if 0 < spr.dirty:
                    for area in spr.dirty_rects:
                        _union_rect = area.move(spr.rect.topleft)
                        _union_rect_collidelist = _union_rect.collidelist
                        _union_rect_union_ip = _union_rect.union_ip
                        i = _union_rect_collidelist(_update)
                        while -1 < i:
                            _union_rect_union_ip(_update[i])
                            del _update[i]
                            i = _union_rect_collidelist(_update)
                        _update_append(_union_rect.clip(_clip))
                        # Update old rects
                        for old_rect in _old_rects[spr]:
                            _union_rect = _rect(old_rect)
                            _union_rect_collidelist = _union_rect.collidelist
                            _union_rect_union_ip = _union_rect.union_ip
                            i = _union_rect_collidelist(_update)
                            while -1 < i:
                                _union_rect_union_ip(_update[i])
                                del _update[i]
                                i = _union_rect_collidelist(_update)
                            _update_append(_union_rect.clip(_clip))
        else:
            _update[:] = [_rect(_clip)]
        # 2. clear using background
        for rec in _update:
            if _bgd is not None:
                _surf_blit(_bgd, rec, rec)
            else:
                pass#_surf_fill(0, rec)
        # 3. draw
        for spr in _sprites:
            if self._use_update and 1 > spr.dirty and spr._visible:
                # sprite not dirty; blit only the intersecting part
                _spr_rect = spr.rect
                if spr.source_rect is not None:
                    _spr_rect = Rect(spr.rect.topleft,
                                     spr.source_rect.size)
                _spr_rect_clip = _spr_rect.clip
                for idx in _spr_rect.collidelistall(_update):
                    # clip
                    clip = _spr_rect_clip(_update[idx])
                    _surf_blit(spr.image,
                               clip,
                               (clip[0] - _spr_rect[0],
                                clip[1] - _spr_rect[1],
                                clip[2],
                                clip[3]),
                               spr.blendmode)
            # dirty sprite
            elif spr._visible:
                _old_rects[spr] = []
                for area in spr.dirty_rects:
                    if spr.source_rect:
                        area.move_ip(spr.source_rect.topleft)
                    _old_rects[spr].append(_surf_blit(spr.image,
                                                      spr.rect.move(area.topleft),
                                                      area,
                                                      spr.blendmode))
            _ret = list(_update)
        # 4. Reset
        _update[:] = []
        _surf.set_clip(_orig_clip)
        for spr in _sprites:
            spr.dirty = 0 if spr.dirty < 2 else 2
            spr.dirty_rects = None
        # 5. Timing update
        delta = pg.time.get_ticks() - start_time
        self._use_update = delta < self._time_threshold
        # 6. Return filtered rectangles
        return filter(bool, _ret)


# Autogroup class
class AutoGroup(PatchedLayeredDirty):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("_time_threshold", 9e9)
        LayeredDirty.__init__(self, *args, **kwargs)

    def reset_update(self):
        self._use_update = False

    @property
    def is_drawn(self):
        return self._use_update

    @property
    def is_dirty(self):
        return any(sprite.dirty for sprite in self)

