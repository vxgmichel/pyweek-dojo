"""Contain the model for the main game state."""

# Imports
from pygame import Rect
from mvctools import BaseModel, xytuple


# Dojo model
class DojoModel(BaseModel):
    """Dojo model for the main game state."""

    size = 200,100

    def init(self):
        self.rect = Rect((0,0), self.size)
        self.player = PlayerModel(self)

    def register_validation(self):
        self.player.jump()

# Player model
class PlayerModel(BaseModel):
    """Player model"""

    air_friction = 0.5, 0.5 # s-1
    gravity = 0, 981 # pixel/s-2
    jump_speed = 0, -300 # pixel/s
    
    def init(self):
        self.resource = self.control.resource
        self.size = self.resource.image.ash.get_size()
        self.rect = Rect((0,0), self.size)
        self.rect.bottomleft = self.parent.rect.bottomleft
        self.speed = xytuple(0,0).map(float)
        self.remainder = xytuple(0,0).map(float)

    @property
    def delta_tuple(self):
        return xytuple(self.delta, self.delta)

    @property
    def is_on_ground(self):
        return self.rect.bottom >= self.parent.rect.bottom

    def jump(self):
        if self.is_on_ground:
            self.speed += self.jump_speed

    def update(self):
        # Get acc
        acc = -self.speed * self.air_friction
        acc += self.gravity
        # Update speed
        self.speed += self.delta_tuple * acc
        if self.is_on_ground:
            self.speed *= 1, self.speed.y<0
            self.rect.bottom = self.parent.rect.bottom
        # Get step
        step = self.delta_tuple * self.speed
        step += self.remainder
        intstep = step.map(round)
        self.remainder = step - intstep
        # Update rect
        self.rect.move_ip(intstep)
        if self.is_on_ground:
            self.rect.bottom = self.parent.rect.bottom
        
    
        
