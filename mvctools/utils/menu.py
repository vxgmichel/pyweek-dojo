from mvctools import BaseModel, BaseView
from mvctools.sprite import ViewSprite, AutoSprite
from mvctools.common import cursoredlist, from_parent, xytuple
from mvctools.utils.text import LineSprite


# Entry model
class EntryModel(BaseModel):

    def init(self, pos, text, callback=None):
        self.text = text
        self.pos = pos
        self.callback = callback

    @property
    def selected(self):
        return self is self.parent.cursor.get()

    def select(self):
        self.parent.cursor.cursor = self.pos

    def activate(self):
        if callable(self.callback):
            return self.callback()

    def shift(self, shift):
        pass

    def register_hover(self):
        self.select()

    def register_click(self):
        self.activate()


# Main Model

class MenuModel(BaseModel):

    entry_data = {}

    def init(self):
        self.entry_dct = {pos: self.generate_entry(pos, data)
                          for pos, data in self.entry_data.items()}
        entry_lst = (value for _, value in sorted(self.entry_dct.items()))
        self.cursor = cursoredlist(entry_lst)

    def generate_entry(self, pos, data):
        model = data[0]
        args = (pos,) + data[1:]
        return model(self, *args)

    def register_hdir(self, x, player=None):
        self.cursor.get().shift(x)

    def register_vdir(self, y, player=None):
        self.cursor.inc(y)

    def register_start(self, down):
        return self.register_activate(down)

    def register_select(self, down):
        self.cursor.inc(down)

    def register_escape(self, down):
        return down

    def register_activate(self, down, player=None):
        if down:
            return self.cursor.get().activate()

    def register_back(self):
        self.cursor[-1].activate()


# Entry sprite
@from_parent(["font_sizes", "font_name", "antialias", "opacity", "reference",
              "colors"])
class EntrySprite(LineSprite):

    alignment = "left"

    def get_max_rect(self):
        font_dir = self.settings.font_dir
        resource = self.resource.getdir(font_dir)
        font = resource.getfile(self.font_name, max(self.font_sizes))
        raw = self.render(font, self.text, self.antialias,
                          self.color, self.background)
        return raw.get_rect()

    @property
    def text(self):
        return self.model.text

    @property
    def font_size(self):
        return self.font_sizes[self.model.selected]

    @property
    def color(self):
        return self.colors[self.model.selected]

    @property
    def pos(self):
        return self.parent.get_child_pos(self.model.pos)


# Bullet sprite
class BulletSprite(AutoSprite):
    # TODO
    pass


# Menu View
class MenuView(BaseView):

    sprite_class_dct = {EntryModel: EntrySprite}

    # Font
    font_sizes = 0, 0
    font_name = ""
    # Renderer
    antialias = False
    colors = "black", "black"
    # Processing
    opacity = 1.0
    alignment = "left"
    # Margins
    interlines = 0, 0
    margins = 0, 0

    def update(self):
        self.rect_dict = {}
        # Get rects
        for sprite in self.group:
            rect = sprite.get_max_rect()
            pos = xytuple(self.interlines)
            pos += 0, rect.h
            pos *= (sprite.model.pos,) * 2
            setattr(rect, self.reference, pos)
            self.rect_dict[sprite.model.pos] = rect
        # Move rects
        if not self.rect_dict:
            return
        x = min(rect.x for rect in self.rect_dict.values())
        y = min(rect.y for rect in self.rect_dict.values())
        for rect in self.rect_dict.values():
            rect.move_ip(xytuple(self.margins) - (x, y))

    @property
    def reference(self):
        if self.alignment in ["center", "centerx"]:
            return "center"
        if self.alignment in ["left", "right"]:
            return "mid" + self.alignment
        raise ValueError('Not a valid alignment')

    def get_child_pos(self, pos):
        try:
            return getattr(self.rect_dict[pos], self.reference)
        except KeyError:
            return self.margins

    @property
    def size(self):
        margins = xytuple(self.margins) * (2, 2)
        try:
            rects = self.rect_dict.values()
            rect = rects[0].unionall(rects[1:])
            return margins + rect.size
        except (IndexError, AttributeError):
            return margins


@from_parent(["font_sizes", "font_name", "antialias", "colors", "opacity",
              "text", "margins", "alignment", "bgd_color", "bgd_image",
              "interlines"])
class ChildrenMenuView(MenuView):
    """"""
    pass


class MenuSprite(ViewSprite):

    # Font
    font_sizes = 0, 0
    font_name = ""
    # Renderer
    antialias = False
    colors = "black", "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0, 0
    reference = "center"
    alignment = "left"
    # Margin
    margins = 0, 0
    interlines = 0, 0
    # Background
    bgd_color = None
    bgd_image = None

    # View
    view_cls = ChildrenMenuView

    def init(self, **kwargs):
        ViewSprite.init(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)
