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

    air_friction = 0.95, 0.95
    gravity = 0, 5
    jump_speed = 0, -50
    
    def init(self):
        self.resource = self.control.resource
        self.size = self.resource.image.ash.get_size()
        self.rect = Rect((0,0), self.size)
        self.rect.bottomleft = self.parent.rect.bottomleft
        self.speed = xytuple(0,0).map(float)

    @property
    def delta_tuple(self):
        return xytuple(self.delta, self.delta)

    def jump(self):
        self.speed += self.jump_speed

    def update(self):
        step = (self.speed * self.delta_tuple).map(round)
        self.rect.move_ip(step)
        
    
        
