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
    key_dct = {pg.K_TAB:    ("jump", 1),
               pg.K_RSHIFT: ("jump", 2),
               pg.K_w:      ("dir",  1),
               pg.K_a:      ("dir",  1),
               pg.K_s:      ("dir",  1),
               pg.K_d:      ("dir",  1),
               pg.K_UP:     ("dir",  2),
               pg.K_DOWN:   ("dir",  2),
               pg.K_LEFT:   ("dir",  2),
               pg.K_RIGHT:  ("dir",  2),
               pg.K_r:      ("reset", None)}
    
    # Key to direction mapping
    dir_dict = {pg.K_w:     (Dir.UP,    1),
                pg.K_a:     (Dir.LEFT,  1),
                pg.K_s:     (Dir.DOWN,  1),
                pg.K_d:     (Dir.RIGHT, 1),
                pg.K_UP:    (Dir.UP,    2),
                pg.K_LEFT:  (Dir.LEFT,  2),
                pg.K_DOWN:  (Dir.DOWN,  2),
                pg.K_RIGHT: (Dir.RIGHT, 2),}

    # Button to action mapping
    button_dct = {0: ("jump", False),
                  3: ("reset",True),}

    # Axis and hat handling
    hat_action =  ("dir", xytuple(1, -1))
    axis_action = ("dir", xytuple(1, +1))

    def init(self):
        """Initialize the joysticks."""
        factory = lambda: None
        self.cache_dct = defaultdict(factory)
        pg.joystick.quit()
        pg.joystick.init()
        self.joysticks = []
        for i in range(pg.joystick.get_count()):
            self.joysticks.append(pg.joystick.Joystick(i))
            self.joysticks[-1].init()

    def handle_event(self, event):
        """Process the different type of events."""
        if event.type == pg.KEYDOWN:
            return self.register_key(event.key, True)
        if event.type == pg.KEYUP:
            return self.register_key(event.key, False)
        if event.type == pg.JOYHATMOTION:
            return self.register_hat(event.value, event.joy+1)
        if event.type == pg.JOYBUTTONDOWN:
            return self.register_button(event.button, event.joy+1, True)
        if event.type == pg.JOYBUTTONUP:
            return self.register_button(event.button, event.joy+1, False)
        if event.type == pg.JOYAXISMOTION:
            return self.register_axis(event.joy, event.joy+1)

    def axis_position(self, arg):
        """Convert axis value to position."""
        return cmp(arg, 0) if abs(arg) >= self.axis_threshold else 0

    def register_key(self, key, down):
        """Register a key strike."""
        action, player = self.key_dct.get(key, (None, None))
        if action is None:
            return
        if player is None:
            if not down: return
            return self.model.register(action)
        if action != "dir":
            return self.model.register(action, player, down)
        return self.register(action, player, self.get_key_direction(player))

    def get_key_direction(self, player):
        """Get direction from current key state."""
        dct = pg.key.get_pressed()
        gen = (direc for key, (direc, play) in self.dir_dict.items()
               if play == player and dct[key])
        return sum(gen, xytuple(0,0))

    def register_hat(self, hat, player):
        """Register a hat event."""
        action, convert = self.hat_action
        return self.register(action, player, convert * hat)

    def register_button(self, button, player, down):
        """Register a button event."""
        action, general = self.button_dct.get(button, (None,None))
        if action and general:
            if not down: return
            return self.model.register(action)
        elif action:
            return self.model.register(action, player, down)

    def register_axis(self, joy, player):
        """Register an axis event."""
        action, convert = self.axis_action
        raw_values = [self.joysticks[joy].get_axis(i) for i in (0,1)]
        direction = convert * map(self.axis_position, raw_values)
        return self.model.register(action, player, direction)
    
            
            
