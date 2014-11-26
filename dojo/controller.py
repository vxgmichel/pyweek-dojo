"""Contain the controller for the main game state."""

# Imports
from mvctools import BaseController, xytuple
from collections import defaultdict
from dojo.common import Dir
import pygame as pg


# Dojo controller
class DojoController(BaseController):
    """COntroller for the main game state."""

    # Threshold for joysticks
    axis_threshold = 0.5

    # Key to action mapping
    key_dct = {pg.K_x:        ("activate", 1),
               pg.K_SPACE:    ("activate", 1),
               pg.K_p:        ("activate", 2),
               pg.K_KP_ENTER: ("activate", 2),
               pg.K_u:        ("reset", None),
               pg.K_ESCAPE:   ("escape", None),}
    
    # Key to direction mapping
    dir_dct = {pg.K_r:     (Dir.UP,    1),
               pg.K_d:     (Dir.LEFT,  1),
               pg.K_f:     (Dir.DOWN,  1),
               pg.K_g:     (Dir.RIGHT, 1),
               pg.K_UP:    (Dir.UP,    2),
               pg.K_LEFT:  (Dir.LEFT,  2),
               pg.K_DOWN:  (Dir.DOWN,  2),
               pg.K_RIGHT: (Dir.RIGHT, 2),}

    # Update key to action
    key_dct.update((key, ('dir', value[1]))
                   for key, value in dir_dct.items())

    # Button to action mapping
    button_dct = {0: ("activate", False),
                  3: ("reset",True),}

    # Axis and hat handling
    hat_action =  "dir", xytuple(1, -1)
    axis_action = "dir", xytuple(1, +1)

    def init(self):
        """Initialize the joysticks."""
        # Init joystick
        pg.joystick.quit()
        pg.joystick.init()
        # Get joysticks
        self.joysticks = []
        for i in range(pg.joystick.get_count()):
            self.joysticks.append(pg.joystick.Joystick(i))
            self.joysticks[-1].init()
        # Players
        self.nb_players = max(pid for _, pid in self.key_dct.values())
        self.nb_players = max(self.nb_players, len(self.joysticks))
        self.players = range(1, self.nb_players + 1)
        # Init direction
        for player in self.players:
            lst = [self.get_key_direction(player),
                   self.get_axis_direction(player),
                   self.get_hat_direction(player)]
            iterator = (direction for direction in lst if any(direction))
            direction = next(iterator, xytuple(0,0))
            self.register("dir", player, direction)
        # Special keys
        dct = pg.key.get_pressed()
        special_keys = (key for key, value in self.key_dct.items()
                        if value[0] == "activate")
        for key in special_keys:
            if dct[key]:
                self.register_key(key, dct[key])

    def handle_event(self, event):
        """Process the different type of events."""
        if event.type == pg.KEYDOWN:
            return self.register_key(event.key, True)
        if event.type == pg.KEYUP:
            return self.register_key(event.key, False)
        if event.type == pg.JOYHATMOTION:
            return self.register_hat(event.joy+1)
        if event.type == pg.JOYBUTTONDOWN:
            return self.register_button(event.button, event.joy+1, True)
        if event.type == pg.JOYBUTTONUP:
            return self.register_button(event.button, event.joy+1, False)
        if event.type == pg.JOYAXISMOTION:
            return self.register_axis(event.joy+1)

    def axis_position(self, arg):
        """Convert axis value to position."""
        return cmp(arg, 0) if abs(arg) >= self.axis_threshold else 0

    def get_key_direction(self, player):
        """Get direction from current key state."""
        dct = pg.key.get_pressed()
        gen = (direc for key, (direc, play) in self.dir_dct.items()
               if play == player and dct[key])
        return sum(gen, xytuple(0,0))

    def get_axis_direction(self, player):
        """Get direction from current key state."""
        _, convert = self.axis_action
        try :
            raw_values = [self.joysticks[player-1].get_axis(i) for i in (0,1)]
        except IndexError:
            raw_values = 0,0
        return convert * map(self.axis_position, raw_values)

    def get_hat_direction(self, player):
        """Get direction from current key state."""
        _, convert = self.hat_action
        try:
            return convert * self.joysticks[player-1].get_hat(0)
        except IndexError:
            return convert * (0, 0)

    def register_key(self, key, down):
        """Register a key strike."""
        action, player = self.key_dct.get(key, (None, None))
        # Ignore
        if action is None:
            return
        # Generic action
        if player is None:
            return self.model.register(action)
        # Player related action
        if action != "dir":
            return self.model.register(action, player, down)
        # Direction action
        direction = self.get_key_direction(player)
        return self.register(action, player, direction)

    def register_hat(self, player):
        """Register a hat event."""
        action, _ = self.hat_action
        # Ignore
        if action is None:
            return
        # Direction action
        direction = self.get_hat_direction(player)
        return self.register(action, player, direction)

    def register_button(self, button, player, down):
        """Register a button event."""
        action, generic = self.button_dct.get(button, (None,None))
        # Ignore
        if action is None:
            return
        # Generic action
        if generic:
            return self.model.register(action)
        # Player related action
        return self.model.register(action, player, down)

    def register_axis(self, player):
        """Register an axis event."""
        action, _ = self.axis_action
        # Ignore
        if action is None:
            return
        # Direction action
        direction = self.get_axis_direction(player)
        return self.register(action, player, direction)
    
            
            
