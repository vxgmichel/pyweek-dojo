import pygame as pg
from mvctools.sprite import AutoSprite
from mvctools.common import cache
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


class ChilrenLineSprite(LineSprite):

    # Font
    
    @property
    def font_size(self):
        return self.parent.font_size
    
    @property
    def font_name(self):
        return self.parent.font_name
    
    # Renderer

    @property
    def text(self):
        return self.parent.get_child_text(self.id)

    @property
    def antialias(self):
        return self.parent.antialias
    
    @property
    def color(self):
        return self.parent.color
    
    # Processing

    @property
    def opacity(self):
        return self.parent.opacity
    
    # Position

    @property
    def pos(self):
        return self.parent.get_child_pos(self.id)

    @property
    def reference(self):
        return self.parent.get_child_reference(self.id)

    def init(self, lid):
        self.id = lid

    # Layer

    def get_layer(self):
        return self.parent.layer + 1



class TextSprite(AutoSprite):

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
    background = None

    def init(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.update_lines()

    def get_child_text(self, lid):
        try: return self.text.splitlines()[lid]
        except IndexError: return ''

    def get_child_reference(self, lid):
        if self.alignment in ["center", "centerx"]:
            return "center"
        if self.alignment in ["left", "right"]:
            return "mid" + self.alignment
        raise ValueError('Not a valid alignment')

    def update_lines(self):
        nb_lines = len(self.text.splitlines())
        for i in range(len(self.children), nb_lines):
            ChilrenLineSprite(self, i)
        for i in range(len(self.children), nb_lines, -1):
            del self.children[i-1]

    def get_child_pos(self, lid):
        # Get children size
        self.update_lines()
        max_size = max(child.size for child in self.children)
        # Get alignment
        attr = self.alignment
        if self.alignment == "center":
            attr += "x"
        # Get coordinates
        x = getattr(self.rect, attr)
        y = self.rect.top + max_size.y * (lid + 0.5)
        y += self.margin * lid
        return x,y

    @property
    def size(self):
        self.update_lines()
        max_size = max(child.size for child in self.children)
        size = max_size * (1, len(self.children))
        return size + (1, len(self.children) * self.margin)
    
    def get_rect(self):
        rect = Rect((0,0), self.size)
        setattr(rect, self.reference, self.pos)
        return rect

    def get_image(self):
        if not self.background:
            return self.image
        image = Surface(self.size)
        image.fill(self.background)
        return image
