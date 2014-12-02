
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

    size = None
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
        size = self.size
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

    def _update(self):
        # Create screen
        self.update_screen()
        # Update
        self.update()
        self.gen_sprites()
        self.group.update()
        # Changes on a transparent background
        if self.screen and self.screen_size != self.screen.get_size():
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
    def screen_size(self):
        if self.size is None:
            return self.screen.get_size()
        return self.size

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
    """A refactored version of LayeredDirty.

    The main difference is that the group can now handle
    a new sprite attribute called **dirty_rects**.
    When **dirty_rects** is not None and the sprite hasn't
    moved, the group will only draw these rectangles.
    This allow sprites to use group in order to chain screens
    while avoiding performance issue.
    """

    @staticmethod
    def _update_rect_list(rect, lst, clip):
        """Append a rectangle to a list using union and clip."""
        i = rect.collidelist(lst)
        while -1 < i:
            rect.union_ip(lst[i])
            del lst[i]
            i = rect.collidelist(lst)
        lst.append(rect.clip(clip))

    def _prepare_sprites(self):
        """Prepare the sprites before drawing.

        Return the corresponding rectangle list.
        """
        return dict((sprite, self._prepare_sprite(sprite))
                    for sprite in self._spritelist)

    def _prepare_sprite(self, sprite):
        """Prepare a sprite before drawing. and

        Return the corresponding rectangle.
        """
        # Aliases
        sprites = self._spritelist
        old_rect_dct = self.spritedict
        use_update = self._use_update
        # Test dirty rects
        try: sprite.dirty_rects
        except AttributeError: sprite.dirty_rects = None
        # Update dirtyness
        if not sprite.dirty and sprite.dirty_rects:
            sprite.dirty = 1
        # Get actual size
        try: size_rect = Rect((0,0), sprite.source_rect.size)
        except AttributeError: size_rect = Rect((0,0), sprite.rect.size)
        # Update structures
        new_rect = size_rect.move(sprite.rect.topleft)
        has_moved = new_rect != old_rect_dct[sprite]
        # Whole rect is dirty
        if not use_update or has_moved or sprite.dirty_rects is None:
            sprite.dirty_rects = [size_rect]
            return new_rect
        # Clip the dirty rects
        for k, area in enumerate(sprite.dirty_rects):
            sprite.dirty_rects[k] = area.clip(size_rect)
        # Return
        return new_rect

    def _get_dirty_rects(self, new_rect_dct, clip):
        """Return the list of the rectangle to draw.

        It uses the new rectangle dictionary and a clip.
        """
        # Full update case
        if not self._use_update:
            return [Rect(clip)]
        rect_lst = self.lostsprites
        # Loop over sprites
        for sprite in self._spritelist:
            new_rect = new_rect_dct[sprite]
            self._update_list_from_sprite(sprite, new_rect, rect_lst, clip)
        # Return
        return rect_lst

    def _update_list_from_sprite(self, sprite, new_rect, rect_lst, clip):
        """Update a directly rectangle list from a sprite.

        It uses the corresponding rectangle and a clip.
        """
        # New dirty rectangles
        if sprite.dirty > 0 and sprite.visible:
            for area in sprite.dirty_rects:
                rect = area.move(sprite.rect.topleft)
                self._update_rect_list(rect, rect_lst, clip)
        # Old rectangle
        if sprite.dirty > 0:
            old_rect = Rect(self.spritedict[sprite])
            has_changed = old_rect and old_rect != new_rect
            if has_changed or not sprite.visible:
                self._update_rect_list(old_rect, rect_lst, clip)

    def _clear_surface(self, rect_lst, surface, bgd=None):
        """Clear a surface using a background and a dirty rectangle list."""
        for rect in rect_lst:
            surface.fill(0, rect)
            if bgd is not None:
                surface.blit(bgd, rect, rect)

    def _draw_sprites(self, surface, update_rect, new_rect_dct):
        """Draw the sprites on a given surface.

        It takes a dirty rect list and the rectangle dictionary.
        """
        # Loop over sprites
        for sprite in self._spritelist:
            new_rect = new_rect_dct[sprite]
            self._draw_sprite(surface, sprite, new_rect, update_rect)

    def _draw_sprite(self, surface, sprite, new_rect, rect_lst):
        """Draw a sprite on a given surface.

        It takes the corresponding rectangle and a dirty rect list.
        """
        # Aliases
        old_rect_dct = self.spritedict
        use_update = self._use_update
        # Intersection
        if use_update and 1 > sprite.dirty and sprite.visible:
            for idx in new_rect.collidelistall(rect_lst):
                rect_clip = new_rect.clip(rect_lst[idx])
                area = rect_clip.move((-new_rect[0], -new_rect[1]))
                surface.blit(sprite.image, rect_clip, area, sprite.blendmode)
        # Dirty sprite
        elif sprite.visible:
            for area in sprite.dirty_rects:
                dest = sprite.rect.move(area.topleft)
                if sprite.source_rect:
                    area.move_ip(sprite.source_rect.topleft)
                surface.blit(sprite.image, dest, area, sprite.blendmode)
        # Reset
        sprite.dirty = 0 if sprite.dirty < 2 else 2
        sprite.dirty_rects = None

    def draw(self, surface, bgd=None):
        """Draw the group on a given surface using an optional background."""
        # Clip
        save_clip = surface.get_clip()
        clip = save_clip if self._clip is None else self._clip
        surface.set_clip(clip)
        # Background
        if bgd is not None:
            self._bgd = bgd
        bgd = self._bgd
        # Prepare sprites
        new_rect_dct = self._prepare_sprites()
        # Time reference
        start_time = pg.time.get_ticks()
        # Find dirty rectangles on screen
        dirty_rects = self._get_dirty_rects(new_rect_dct, clip)
        # Clear the surface
        self._clear_surface(dirty_rects, surface, bgd)
        # Draw on the surface
        self._draw_sprites(surface, dirty_rects, new_rect_dct)
        # Reset
        self.lostsprites = []
        self.spritedict = new_rect_dct
        surface.set_clip(save_clip)
        # Timing update
        delta = pg.time.get_ticks() - start_time
        self._use_update = delta < self._time_threshold
        # Return filtered rectangles
        return filter(bool, dirty_rects)

    def set_clip(self, screen_rect=None):
        """ Clip the area where to draw."""
        if self._clip != screen_rect:
            self._use_update = False
        self._clip = screen_rect



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

