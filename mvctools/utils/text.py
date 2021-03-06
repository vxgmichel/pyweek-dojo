import pygame as pg
from mvctools.sprite import AutoSprite
from mvctools.common import cache_method, xytuple, from_parent
from mvctools.sprite import ViewSprite
from mvctools.view import BaseView
from pygame import Color, Rect


def opacify(source, opacity):
    surface = source.convert_alpha()
    if opacity < 1:
        color = 255, 255, 255, int(255 * opacity)
        surface.fill(color, special_flags=pg.BLEND_RGBA_MULT)
    return surface

def render(font, text, antialias, color, background):
    if not font or not text:
        return Surface((0,0))
    args = text, antialias, Color(color)
    if background:
        args += Color(background)
    return font.render(*args)


class LineSprite(AutoSprite):

    # Font
    font_size = 0
    font_name = ""
    # Renderer
    text = ""
    antialias = False
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0, 0
    reference = "center"
    # Background
    background = None

    opacify = cache_method(opacify, static=True)
    render = cache_method(render,  static=True)

    def init(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def font(self):
        font_dir = self.settings.font_dir
        resource = self.resource.getdir(font_dir)
        return resource.getfile(self.font_name, self.font_size)

    def get_image(self):
        raw = self.render(self.font, self.text, self.antialias,
                          self.color, self.background)
        return self.opacify(raw, self.opacity)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)


@from_parent(["font_size", "font_name", "antialias",
              "color", "opacity", "reference"])
class ChilrenLineSprite(LineSprite):

    @property
    def text(self):
        return self.parent.get_child_text(self.id)

    @property
    def pos(self):
        return self.parent.get_child_pos(self.id)

    @property
    def background(self):
        if not self.parent.bgd_image:
            return None
        return self.parent.bgd_color

    def init(self, lid):
        self.id = lid


class TextView(BaseView):

    # Font
    font_size = 0
    font_name = ""
    # Renderer
    text = ""
    antialias = False
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    alignment = "left"
    # Interline
    interline = 0
    # Margins
    margins = 0, 0

    def init(self):
        self.lines = []

    def update(self):
        self.update_lines()
        self.max_width = 2 * self.margins[0]
        if self.lines:
            self.max_width += max(child.get_image().get_width()
                                  for child in self.lines)

    def get_child_text(self, lid):
        try:
            return self.text.splitlines()[lid]
        except IndexError:
            return ''

    @property
    def reference(self):
        if self.alignment in ["center", "centerx"]:
            return "midtop"
        if self.alignment in ["left", "right"]:
            return "top" + self.alignment
        raise ValueError('Not a valid alignment')

    def update_lines(self):
        nb_lines = len(self.text.splitlines())
        for i in range(len(self.lines), nb_lines):
            self.lines.append(ChilrenLineSprite(self, i))
        for i in range(len(self.lines), nb_lines, -1):
            self.lines[-1].delete()
            del self.lines[-1]

    def get_child_pos(self, lid):
        previous = self.lines[lid-1] if lid else None
        interline = xytuple(0, self.interline)
        # Left aligment
        if self.alignment == "left":
            if previous:
                return interline + previous.bottomleft
            return self.margins
        # Centered aligment
        if self.alignment == "center":
            if previous:
                return interline + previous.midbottom
            return xytuple(self.margins) + (self.max_width/2, 0)
        # Right aligment
        if self.alignment == "right":
            if previous:
                return interline + previous.bottomright
            return xytuple(self.margins) + (self.max_width, 0)

    @property
    def size(self):
        if not self.group:
            return xytuple(0, 0)
        x = max(sprite.rect.right for sprite in self.group)
        y = max(sprite.rect.bottom for sprite in self.group)
        return xytuple(x, y) + self.margins


@from_parent(["font_size", "font_name", "antialias", "color", "opacity",
              "text", "bgd_color", "bgd_image", "margins", "alignment",
              "interline"])
class ChildrenTextView(TextView):
    pass


class TextSprite(ViewSprite):

    # Font
    font_size = 0
    font_name = ""
    # Renderer
    text = ""
    antialias = False
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0, 0
    reference = "center"
    alignment = "left"
    # Margin
    margins = 0, 0
    interline = 0
    # Background
    bgd_color = None
    bgd_image = None
    # View
    view_cls = ChildrenTextView

    def init(self, **kwargs):
        ViewSprite.init(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)
