import pygame as pg
from mvctools.sprite import AutoSprite
from mvctools.common import cache
from pygame import Color, transform


class RendererSprite(AutoSprite):
    
    font_folder = "font"
    font_name = ""
    font_ratio = 0.0
    font_color = "black"
    font_opacity = 1.0
  
    def init(self):
        self.renderer = self.build_renderer()

    @property
    def font_size(self):
        return int(self.settings.height * self.font_ratio)

    def apply_opacity(self, surface, opacity=None):
        if opacity is None:
            opacity = self.font_opacity
        color = 255, 255, 255, int(255 * opacity)
        surface.fill(color, special_flags=pg.BLEND_RGBA_MULT)
        return surface

    def build_renderer(self, name=None, size=None, color=None,
                             native_ratio=None, cached=True):
        # Check arguments
        name = self.font_name if name is None else name
        size = self.font_size if size is None else size
        color = self.font_color if color is None else color
        if isinstance(color, basestring):
            color = Color(color)
        if native_ratio is None:
            native_ratio = self.settings.native_ratio
        # Load the font
        font = self.resource.getdir(self.font_folder).getfile(name, size)
        # Get the renderer
        def renderer(text, opacity=None, native_ratio=native_ratio):
            # Render the text
            raw = font.render(text, False, color).convert_alpha()
            # No native ratio case
            if native_ratio is None:
                return self.apply_opacity(raw, opacity)
            # Ratio between native ratio and current ratio
            current_ratio = float(self.settings.width)/self.settings.height
            ratio = current_ratio/native_ratio
            # Already native case
            if ratio == 1:
                return self.apply_opacity(raw, opacity)
            # Scaling
            img_size = int(raw.get_width() * ratio), raw.get_height()
            img = transform.smoothscale(raw, img_size)
            return self.apply_opacity(img, opacity)
        # Activate caching if needed
        if cached:
            return cache(renderer)
        return renderer
