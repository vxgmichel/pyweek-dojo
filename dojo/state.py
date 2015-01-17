from mvctools import BaseState, BaseModel, BaseView, AutoSprite
from mvctools.utils import TextSprite, EntryModel, MenuModel, MenuSprite
from mvctools.utils import TwoPlayersController, PlayerAction
from mvctools import Dir, NextStateException, Timer, from_gamedata

from dojo.controller import DojoController
from dojo.view import DojoView
from dojo.model import DojoModel, TitleMenuModel

import pygame
from random import choice, expovariate


# No player model
class NoPlayerModel(DojoModel):

    display_scores = False
    display_controls = False
    ai_speed = 1

    def init(self):
        DojoModel.init(self)
        self.reset_timer = Timer(self, stop=3, callback=self.reset)
        for i in (1, 2):
            self.room.players[i].jump_timer = None
        
    def post_update(self):
        """Set up AI for both players and disable bullet time.
        """
        # Disable bullet time
        if self.room.time_speed:
            self.room.time_speed = 1.0
        # Wait if gameover
        if self.room.gameover:
            self.reset_timer.start()
            return
        # IA
        for player in self.room.players.values():
            # Load
            if player.fixed and not player.prepared:
                player.load()
            # Pick a direction
            if player.fixed and not any(player.current_dir):
                player.register_dir(choice(Dir.DIRS))
            # Delay a jump
            if player.fixed and player.prepared and not player.jump_timer:
                player.jump_timer = Timer(self,
                                          stop=expovariate(self.ai_speed),
                                          callback=self.gen_callback(player)
                                          ).start()
            # Reset direction
            if not player.fixed:
                player.register_dir(Dir.NONE)

    def gen_callback(self, player):
        def callback(self, arg=None):
            player.jump()
            player.jump_timer = None
        return callback

    def reset(self, arg=None):
        self.control.register_next_state(type(self.state))
        raise NextStateException


# Title Screen Model
class DojoMainModel(NoPlayerModel):

    def init(self):
        NoPlayerModel.init(self)
        self.menu.change_parent(self.room)

    @from_gamedata
    def menu(self):
        return TitleMenuModel(self.room)

    def register(self, *args, **kwargs):
        """Forward action to the menu."""
        return self.menu.register(*args, **kwargs)


# Info Model
class InfoModel(DojoModel):

    display_controls = True
    display_scores = False
    
    def init(self):
        DojoModel.init(self)

    @from_gamedata
    def menu(self):
        return TitleMenuModel(self.room)

    def register(self, action, down, *args, **kwargs):
        """Forward action to the menu."""
        actions = ["start", "select", "escape", "activate", "back"]
        if action in actions and down:
           self.control.register_next_state(self.control.first_state)
           return True
            

# One Player Model
class OnePlayerModel(DojoModel):

    ai_speed = 3

    def init(self):
        DojoModel.init(self)
        self.room.players[2].jump_timer = None

    def register(self, action, arg, player=None):
        """Escape to pass and remap player 2 events on player 1."""
        if player is None:
            return self.room.register(action, arg)
        return self.room.register(action, arg, 1)

    def post_update(self):
        """Set up AI for player 2."""
        DojoModel.post_update(self)
        # Wait if gameover
        if self.room.gameover:
            return
        # Load
        player = self.room.players[2]
        if player.fixed and not player.prepared:
            player.load()
        # Pick a direction
        if player.fixed and not any(player.current_dir):
            player.register_dir(choice(Dir.DIRS))
        # Delay a jump
        if player.fixed and player.prepared and not player.jump_timer:
            player.jump_timer = Timer(self,
                                      stop=expovariate(2),
                                      callback=self.gen_callback(player)
                                      ).start()
        # Reset direction
        if not player.fixed:
            player.register_dir(Dir.NONE)

    def gen_callback(self, player):
        def callback(self, arg=None):
            player.jump()
            player.jump_timer = None
        return callback

# Informative state
class InfoState(BaseState):
    model_class = InfoModel
    controller_class = DojoController
    view_class = DojoView

# One player state
class OnePlayerState(BaseState):
    model_class = OnePlayerModel
    controller_class = DojoController
    view_class = DojoView

# Two players state
class TwoPlayersState(BaseState):
    model_class = DojoModel
    controller_class = DojoController
    view_class = DojoView

# Dojo main state
class DojoMainState(BaseState):
    model_class = DojoMainModel
    controller_class = DojoController
    view_class = DojoView
    entries = [("1 player", OnePlayerState),
               ("2 players", TwoPlayersState),
               ("controls", InfoState),
               ("settings", None),
               ("quit", None)]
