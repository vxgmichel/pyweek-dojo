from mvctools import BaseController, xytuple
from collections import defaultdict
from dojo.common import Dir
import pygame as pg

# Controller

class DojoController(BaseController):

    axis_threshold = 0.5

    key_dct = {pg.K_SPACE:  ("jump", 1),
               pg.K_UP:     ("dir",  1),
               pg.K_DOWN:   ("dir",  1),
               pg.K_LEFT:   ("dir",  1),
               pg.K_RIGHT:  ("dir",  1),}

    dir_dict = {pg.K_UP:     Dir.UP,
                pg.K_DOWN:   Dir.DOWN,
                pg.K_LEFT:   Dir.LEFT,
                pg.K_RIGHT:  Dir.RIGHT,}

    button_dct = {0: "jump",
                  2: "jump",
                 }

    hat_action =  ("dir", xytuple(1, -1))
    axis_action = ("dir", xytuple(1, +1))

    def init(self):
        factory = lambda: None
        self.cache_dct = defaultdict(factory)
        pg.joystick.quit()
        pg.joystick.init()
        self.joysticks = []
        for i in range(pg.joystick.get_count()):
            self.joysticks.append(pg.joystick.Joystick(i))
            self.joysticks[-1].init()

    def handle_event(self, event):
        if super(DojoController, self).handle_event(event):
            return True
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
        return cmp(arg, 0) if abs(arg) >= self.axis_threshold else 0

    def register_key(self, key, down):
        action, player = self.key_dct[key]
        if player is None:
            return self.model.register(action)
        if action != "dir":
            return self.model.register(action, player, down)
        return self.register(action, player, self.get_key_direction())

    def get_key_direction(self):
        dct = pg.key.get_pressed()
        gen = (value for key, value in self.dir_dict.items() if dct[key])
        return sum(gen, xytuple(0,0))

    def register_hat(self, hat, player):
        action, convert = self.hat_action
        self.register(action, player, convert * hat)

    def register_button(self, button, player, down):
        action = self.button_dct.get(button)
        if action:
            self.model.register(action, player, down)

    def register_axis(self, joy, player):
        action, convert = self.axis_action
        raw_values = [self.joysticks[joy].get_axis(i) for i in (0,1)]
        direction = convert * map(self.axis_position, raw_values)
        self.model.register(action, player, direction)
    
            
            
