from mvctools import BaseState, BaseModel, BaseView, AutoSprite
from mvctools.utils import TextSprite, EntryModel, MenuModel, MenuSprite
from mvctools.utils import TwoPlayersController, PlayerAction
from mvctools import Dir, NextStateException

from dojo.controller import DojoController
from dojo.view import DojoView
from dojo.model import DojoModel

import pygame
from random import choice, random
    
# Zero Player Model
class ZeroPlayerModel(DojoModel):

    def register(self, action, down, *args):
        """Pass the demo."""
        actions = ["start", "select", "escape", "activate", "back"]
        if down and action in actions:
            self.control.register_next_state(OnePlayerState)
            try:
                del self.control.gamedata.score_dct
            except AttributeError:
                pass
            return True

    def post_update(self):
        """Set up AI for both players and disable bullet time.
        """
        for player in self.room.players.values():
            if player.fixed and not player.prepared:
                player.load()
            if player.fixed and not any(player.current_dir):
                player.register_dir(choice(Dir.DIRS))
            if player.fixed and player.prepared and random() < 0.05:
                player.jump()
            if not player.fixed:
                player.register_dir(Dir.NONE)
            if player.ko and random() < 0.01:
                self.control.register_next_state(type(self.state))
                raise NextStateException
            if self.room.time_speed:
                self.room.time_speed = 1.0

# One Player Model
class OnePlayerModel(DojoModel):

    def register(self, action, arg, player=None):
        """Escape to pass and remap player 2 events on player 1."""
        if arg and action == "escape":
            self.control.register_next_state(TwoPlayerState)
            try:
                del self.control.gamedata.score_dct
            except AttributeError:
                pass
            return True
        if player is None:
            return self.room.register(action, arg)
        return self.room.register(action, arg, 1)

    def post_update(self):
        """Set up AI for player 2."""
        DojoModel.post_update(self)
        player = self.room.players[2]
        if player.fixed and not player.prepared:
            player.load()
        if player.fixed and not any(player.current_dir):
            player.register_dir(choice(Dir.DIRS))
        if player.fixed and player.prepared and random() < 0.05:
            player.jump()
        if not player.fixed:
            player.register_dir(Dir.NONE)

# Zero Player state
class ZeroPlayerState(BaseState):
    model_class = ZeroPlayerModel
    controller_class = DojoController
    view_class = DojoView

# One Player state
class OnePlayerState(BaseState):
    model_class = OnePlayerModel
    controller_class = DojoController
    view_class = DojoView

# Two Player state
class TwoPlayerState(BaseState):
    model_class = DojoModel
    controller_class = DojoController
    view_class = DojoView
