import pygame as pg
from mvctools.sprite import AutoSprite
from mvctools.common import cache, xytuple
from mvctools.sprite import ViewSprite
from mvctools import BaseView
from pygame import Color, Rect

def from_parent(lst):
    # Getter generator
    gen_getter = lambda attr: lambda self: getattr(self.parent, attr)
    # Decorator
    def decorator(cls):
        # Loop over attributes
        for attr in lst:
            # Set property
            setattr(cls, attr, property(gen_getter(attr)))
        return cls
    # Return
    return decorator

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
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0,0
    reference = "center"
    # Background
    background = None

    opacify = cache(opacify, static=True)
    render =  cache(render,  static=True)

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



@from_parent(["font_size", "font_name", "antialias", "color", "opacity"])
class ChilrenLineSprite(LineSprite):

    @property
    def text(self):
        return self.parent.get_child_text(self.id)

    @property
    def pos(self):
        return self.parent.get_child_pos(self.id)

    @property
    def reference(self):
        return self.parent.get_child_reference(self.id)

    def init(self, lid):
        self.id = lid

class TextView(BaseView):
    
    # Font 
    font_size = 0
    font_name = ""
    # Renderer
    text = ""
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0,0
    reference = "center"
    alignment = "left"
    # Margin
    margin = 0

    def init(self):
        self.lines = []

    def update(self):
        self.update_lines()

    def get_child_text(self, lid):
        try: return self.text.splitlines()[lid]
        except IndexError: return ''

    def get_child_reference(self, lid):
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
            self.lines.kill()
            
    def get_child_pos(self, lid):
        previous = self.lines[lid-1] if lid else None
        margin = xytuple(0, self.margin)
        # Left aligment
        if self.alignment == "left":
            if previous:
                return margin + previous.bottomleft
            return 0,0
        # Centered aligment
        if self.alignement == "center":
            if previous:
                return margin + previous.midbottom
            max_width = max(child.rect.w for child in self.lines)
            return max_width/2, 0
        # Right aligment
        elif self.alignment == "right":
            if previous:
                return margin + previous.bottomright
            return max_width, 0


@from_parent(["font_size", "font_name", "antialias", "color", "opacity",
              "text", "bgd_color", "bgd_image", "margin"])
class ChildrenTextView(TextView):
    pass

class TextSprite(ViewSprite):

    # Font 
    font_size = 0
    font_name = ""
    # Renderer
    text = ""
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0,0
    reference = "center"
    alignment = "left"
    # Margin
    margin = 0 
    # Background
    bgd_color = None
    bgd_image = None
    # View
    view_cls = ChildrenTextView

    def init(self, **kwargs):
        ViewSprite.init(self)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def screen_size(self):
        if not self.view.group:
            return xytuple(0, 0)
        x = max(sprite.rect.right for sprite in self.view.group)
        y = max(sprite.rect.bottom for sprite in self.view.group)
        return xytuple(x, y)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)
