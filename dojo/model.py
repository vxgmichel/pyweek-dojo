"""Contain the model for the main game state."""

# Imports
from pygame import Rect
from mvctools import BaseModel, xytuple
from dojo.common import Dir

# Dojo model
class DojoModel(BaseModel):
    """Dojo model for the main game state."""

    size = 200,100

    def init(self):
        self.rect = Rect((0,0), self.size)
        self.players = {1:PlayerModel(self)}

    def register_jump(self, player, down):
        player = self.players[player]
        if down: player.jump()

    def register_dir(self, player, direction):
        self.players[player].dir = direction

        
        
# Player model
class PlayerModel(BaseModel):
    """Player model"""

    air_friction = 0.5, 0.5 # s-1
    gravity = 0, 981 # pixel/s-2
    load_speed = 800 # pixel/s-2
    max_loading_speed = 1000 # pixel/s

    collide_dct = {"bottom": Dir.DOWN,
                   "left": Dir.LEFT,
                   "right": Dir.RIGHT,
                   "top": Dir.UP}
    
    def init(self):
        self.resource = self.control.resource
        self.size = self.resource.image.ash.get_size()
        self.rect = Rect((0,0), self.size)
        self.rect.bottomleft = self.parent.rect.bottomleft
        self.speed = self.remainder = self.loading_speed = xytuple(0.0,0.0)
        self.dir = Dir.NONE
        self.pos = Dir.DOWN
        self.fixed = True

    @property
    def delta_tuple(self):
        return xytuple(self.delta, self.delta)

    def jump(self):
        if self.fixed:
            # Get coeff
            sign = lambda arg: cmp(arg, 0)
            dir_coef = self.dir - self.pos
            dir_coef = dir_coef.map(sign)
            if sum(self.dir*self.pos) <= 0 and any(dir_coef) and any(self.dir):
                dir_coef /= (abs(dir_coef),)*2
                # Update speed
                self.speed += self.loading_speed * dir_coef
            # Update status
            self.pos = Dir.NONE
            self.fixed = False
            self.loading_speed *= (0,0)

    def update_collision(self):
        collide_dct = dict(self.collide_dct.items())
        while not self.parent.rect.contains(self.rect):
            self.fixed = True
            dct = {}
            for attr, direc in collide_dct.items():
                rect = self.rect.copy()
                value = getattr(self.parent.rect, attr)
                setattr(rect, attr, value)
                distance = abs(xytuple(*rect.topleft) - self.rect.topleft)
                dct[distance] = rect, direc, attr
            self.rect, self.pos, attr = dct[min(dct)]
            del collide_dct[attr]
            

    def update(self):
        # Get acc
        acc = -self.speed * self.air_friction
        acc += self.gravity
        # Update speed
        self.speed += self.delta_tuple * acc
        if self.fixed:
            self.speed *= 0,0
        # Update loading speed
        if self.fixed:
            self.loading_speed += self.delta_tuple * ((self.load_speed,)*2)
        self.loading_speed = max(self.loading_speed, self.max_loading_speed)
        # Get step
        step = self.delta_tuple * self.speed
        step += self.remainder
        intstep = step.map(round)
        self.remainder = step - intstep
        # Update rect
        self.rect.move_ip(intstep)
        self.update_collision()
        
    
        
