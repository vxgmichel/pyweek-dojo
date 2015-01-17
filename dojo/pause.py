from mvctools import BaseState, BaseModel, BaseView, AutoSprite
from mvctools.utils import TextSprite, EntryModel, MenuModel, MenuSprite
from mvctools.utils import TwoPlayersController, PlayerAction
import pygame


# Controller
class PauseController(TwoPlayersController):
    # Remapping
    button_dct = dict(TwoPlayersController.button_dct)
    # Add escape on Start button
    button_dct[7] = PlayerAction.ESCAPE, False


class PauseModel(MenuModel):

    @property
    def entry_data(self):
        return {0: (EntryModel, "resume", self.resume),
                1: (EntryModel, "main menu", self.reset),
                2: (EntryModel, "quit", self.quit)}

    def register_escape(self, down):
        return down

    def resume(self):
        return True

    def reset(self):
        del self.control.gamedata.score_dct
        state = self.control.pop_state()
        self.control.register_next_state(self.control.first_state)
        return True

    def quit(self):
        raise SystemExit


class PauseSprite(MenuSprite):

    # Entries
    font_sizes = 38, 48
    font_name = "visitor2"
    colors = "#909090", "#F0F0F0"
    bgd_color = "#282828"
    alignment = "center"
    margins = 20, 10
    interlines = 0, 10

    # Position
    reference = "center"
    position_ratio = 0.5, 0.5
    size_ratio = 0.5

    # Layer
    def get_layer(self):
        return 1

    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)


# View class
class PauseView(BaseView):
    shade_ratio = 0.5
    sprite_class_dct = {PauseModel: PauseSprite}
    size = 640, 360

    def create_background(self):
        bgd = self.resource.scale(pygame.display.get_surface(), self.screen_size)
        color = (255*self.shade_ratio,)*3
        bgd.fill(color, special_flags=pygame.BLEND_MULT)
        return bgd


# Loading state
class PauseState(BaseState):
    model_class = PauseModel
    controller_class = PauseController
    view_class = PauseView
