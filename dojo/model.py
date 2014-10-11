"""Contain the model for the main game state."""

# Imports
from pygame import Rect, Color
from mvctools import BaseModel, xytuple, Timer
from dojo.common import Dir

# Dojo model
class DojoModel(BaseModel):
    """Dojo model for the main game state."""

    ref = "room"
    damping = 0.8

    def init(self):
        self.resource = self.control.resource
        self.size = self.resource.image.get(self.ref).get_size()
        self.rect = Rect((0,0), self.size)
        self.border = BorderModel(self)
        self.players = {i:PlayerModel(self, i) for i in (1,2)}
        self.coliding = False


    def register_jump(self, player, down):
        player = self.players[player]
        player.load() if down else player.jump()
            

    def register_dir(self, player, direction):
        self.players[player].control_dir = direction

    def update(self):
        hit = {}
        for i in (1,2):
            j = 2 if i==1 else 1
            lst = [self.players[j].legs, self.players[j].body, self.players[j].head]
            index = self.players[i].legs.collidelist(lst)
            hit[i] = index > 0
            tie = not index
        colide = tie or any(hit.values())
        if colide and not self.coliding:
            if hit[1]: print "1 hit 2 !!"
            if hit[2]: print "2 hit 1 !!"
            for player in self.players.values():
                player.speed *= (-self.damping,)*2
                self.coliding = True
        elif not colide:
            self.coliding = False


# Border modem
class BorderModel(BaseModel):

    offset = -14, -15

    def init(self):
        self.rect = self.parent.rect.inflate(*self.offset)


class RectModel(BaseModel):

    def init(self, attr, color):
        self.attr = attr
        self.color = color
        
    @property
    def rect(self):
        return getattr(self.parent, self.attr)
    
# Player model
class PlayerModel(BaseModel):
    """Player model"""

    # Physics
    air_friction = 0.5, 0.5  # s-1
    gravity = 0, 981         # pixel/s-2
    load_speed = 600         # pixel/s-2
    init_speed = 200         # pixel/s
    max_loading_speed = 1000 # pixel/s

    # Animation
    period = 2.0 # s
    load_factor_min = 5
    load_factor_max = 10

    # Debu
    display_hitbox = False

    collide_dct = {Dir.DOWN: "bottom",
                   Dir.LEFT: "left",
                   Dir.RIGHT: "right",
                   Dir.UP: "top",}

    attr_dct =   {Dir.NONE:  "center",
                  Dir.DOWN:  "midbottom",
                  Dir.LEFT:  "midleft",
                  Dir.RIGHT: "midright",
                  Dir.UP:    "midtop",
                  ( 1,  1):  "bottomright",
                  ( 1, -1):  "topright",
                  (-1,  1):  "bottomleft",
                  (-1, -1):  "topleft",}

    ref = "player_1"
    
    def init(self, pid):
        self.id = pid
        self.border = self.parent.border
        self.resource = self.control.resource
        self.size = self.resource.image.get(self.ref)[0].get_size()
        self.rect = Rect((0,0), self.size)
        if pid == 1:
            self.rect.bottomleft = self.border.rect.bottomleft
        else:
            self.rect.bottomright = self.border.rect.bottomright
        self.speed = self.remainder = xytuple(0.0,0.0)
        self.control_dir = Dir.NONE
        self.pos = Dir.DOWN
        self.fixed = True
        self.loading = False
        self.loading_speed = self.init_speed
        self.timer = Timer(self, stop=self.period, periodic=True)
        self.timer.start()
        if self.display_hitbox:
            RectModel(self, "head", Color("red"))
            RectModel(self, "body", Color("green"))
            RectModel(self, "legs", Color("blue"))

    @property
    def delta_tuple(self):
        return xytuple(self.delta, self.delta)


    def load(self):
        self.loading = True

    def jump(self):
        if self.fixed:
            dir_coef = self.current_dir
            if any(dir_coef):
                dir_coef /= (abs(dir_coef),)*2
                # Update speed
                self.speed += dir_coef * ((self.loading_speed,)*2)
            # Update status
            if self.pos != Dir.DOWN or any(dir_coef):
                self.pos = Dir.NONE
                self.fixed = False
        # Reset loading
        self.loading = False
        self.loading_speed = self.init_speed

    def update_collision(self):
        collide_dct = dict(self.collide_dct.items())
        while not self.border.rect.contains(self.rect):
            self.fixed = True
            dct = {}
            for direc, attr in collide_dct.items():
                rect = self.rect.copy()
                value = getattr(self.border.rect, attr)
                setattr(rect, attr, value)
                distance = abs(xytuple(*rect.topleft) - self.rect.topleft)
                dct[distance] = rect, direc, attr
            self.rect, self.pos, _ = dct[min(dct)]
            del collide_dct[self.pos]

    @property
    def loading_ratio(self):
        res = float(self.loading_speed - self.init_speed)
        return res / (self.max_loading_speed - self.init_speed)

    @property
    def current_dir(self):
        # Static case
        if self.fixed:
            if not any(self.control_dir) or \
               sum(self.control_dir*self.pos) > 0:
                return xytuple(0,0)
            current_dir = self.control_dir - self.pos
            sign = lambda arg: cmp(arg, 0)
            return current_dir.map(sign)
        # Dynamic case
        if not any(self.speed):
            return xytuple(0,0)
        norm = self.speed / ((abs(self.speed),)*2)
        _, x, y = min((abs(norm - (x,y)), x, y)
                          for x in range(-1,2)
                              for y in range(-1,2))
        return xytuple(x,y)

    def get_rect_from_dir(self, direction):
        size = xytuple(*self.size) / (2,2)
        attr = self.attr_dct[direction]
        rect = Rect((0,0), size)
        value = getattr(self.rect, attr)
        setattr(rect, attr, value)
        return rect

    @property
    def head(self):
        if self.fixed:       
            return self.get_rect_from_dir(self.pos * (-1,-1))
        return self.get_rect_from_dir(self.current_dir * (-1,-1))

    @property
    def body(self):
        return self.get_rect_from_dir(Dir.NONE)

    @property
    def legs(self):
        if self.fixed:       
            return self.get_rect_from_dir(self.pos)
        return self.get_rect_from_dir(self.current_dir)

    def update(self):
        # Get acc
        acc = -self.speed * self.air_friction
        acc += self.gravity
        # Update speed
        self.speed += self.delta_tuple * acc
        if self.fixed:
            self.speed *= 0,0
        # Update loading speed
        if self.fixed and self.loading:
            self.loading_speed += self.delta * self.load_speed
        self.loading_speed = min(self.loading_speed, self.max_loading_speed)
        # Get step
        step = self.delta_tuple * self.speed
        step += self.remainder
        intstep = step.map(round)
        self.remainder = step - intstep
        # Update rect
        self.rect.move_ip(intstep)
        self.update_collision()
        # Update timer
        delta = self.load_factor_max - self.load_factor_min
        ratio = self.load_factor_min + self.loading_ratio * delta
        self.timer.start(ratio if self.loading_ratio else 1)
        
    
        
