from mvctools import BaseState, BaseModel, BaseView, AutoSprite
from mvctools.utils import TextSprite, EntryModel, MenuModel, MenuSprite
from mvctools.utils import TwoPlayersController, PlayerAction
from mvctools import Dir

from dojo.controller import DojoController
from dojo.view import DojoView
from dojo.model import DojoModel

import pygame
from random import choice, random

# Dojo state
class DojoState(BaseState):
    """Dojo main game state."""

    controller_class = DojoController
    model_class = DojoModel
    view_class = DojoView
    
# Demo Model
class DemoModel(DojoModel):

    def register(self, action, down, *args):
        """Pass the demo."""
        actions = ["start", "select", "escape", "activate", "back"]
        if down and action in actions:
            self.control.register_next_state(DojoState)
            del self.control.gamedata.score_dct
            return True

    def post_update(self):
        for player in self.room.players.values():
            if player.fixed and not player.prepared:
                player.load()
            if player.fixed and not any(player.current_dir):
                player.register_dir(choice(Dir.DIRS))
            if player.fixed and player.prepared and random() < 0.05:
                player.jump()
            if not player.fixed:
                player.register_dir(Dir.NONE)
            player.ko = False
            if self.room.time_speed:
                self.room.time_speed = 1.0

# Demo state
class DemoState(BaseState):
    model_class = DemoModel
    controller_class = TwoPlayersController
    view_class = DojoView
