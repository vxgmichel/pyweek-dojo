"""Contain the model for the main game state."""

# Imports
from pygame import Rect, Color
from mvctools import BaseModel, xytuple, Timer
from dojo.common import Dir

# Dojo model
class DojoModel(BaseModel):
    """Dojo model for the main game state."""
    
    # Resource to get the model size
    ref = "room"

    # Damping when two players collide
    damping = 0.8

    def init(self):
        """Initialize players and borders."""
        self.resource = self.control.resource
        self.size = self.resource.image.get(self.ref).get_size()
        self.rect = Rect((0,0), self.size)
        self.border = BorderModel(self)
        self.players = {i:PlayerModel(self, i) for i in (1,2)}
        self.colliding = False


    def register_jump(self, player, down):
        """Register a jump from the controller."""
        player = self.players[player]
        player.load() if down else player.jump()

    def register_reset(self):
        """Register a reset from the controller."""
        self.control.register_next_state(type(self.state))
        return True
            
    def register_dir(self, player, direction):
        """Register a direction change from the contromller."""
        self.players[player].control_dir = direction

    def update(self):
        """Detect collision between the 2 players."""
        hit = {}
        for i in (1,2):
            j = 2 if i==1 else 1
            lst = [self.players[j].legs, self.players[j].body, self.players[j].head]
            index = self.players[i].legs.collidelist(lst)
            hit[i] = index > 0
            tie = not index
        collide = tie or any(hit.values())
        if collide and not self.colliding:
            if hit[1]:
                self.players[2].set_ko()
            if hit[2]:
                self.players[1].set_ko()
            for player in self.players.values():
                player.speed *= (-self.damping,)*2
                self.colliding = True
        elif not collide:
            self.colliding = False


# Border modem
class BorderModel(BaseModel):
    """Border model. Useful to detect collision."""

    # Offset compare to the room size
    offset = -14, -15

    def init(self):
        """Compute the border rectangle."""
        self.rect = self.parent.rect.inflate(*self.offset)

# Rect
class RectModel(BaseModel):
    """Rectangle model for debug purposes."""

    def init(self, attr, color):
        """Initialize from a parent attribute name and a color."""
        self.attr = attr
        self.color = color
        
    @property
    def rect(self):
        """Rectangle property."""
        return getattr(self.parent, self.attr)
    
# Player model
class PlayerModel(BaseModel):
    """Player model. Most of the gameplay is handled here."""

    # Physics
    air_friction = 0.5, 0.5  # s-1
    gravity = 0, 981         # pixel/s-2
    load_speed = 600         # pixel/s-2
    init_speed = 200         # pixel/s
    max_loading_speed = 1000 # pixel/s

    # Animation
    period = 2.0         # s
    load_factor_min = 5  # period-1
    load_factor_max = 10 # period-1

    # Debug
    display_hitbox = False

    # Direction to Rect attributes for wall collision
    collide_dct = {Dir.DOWN: "bottom",
                   Dir.LEFT: "left",
                   Dir.RIGHT: "right",
                   Dir.UP: "top",}

    # Direction to Rect attributes for player collision
    attr_dct =   {Dir.NONE:  "center",
                  Dir.DOWN:  "midbottom",
                  Dir.LEFT:  "midleft",
                  Dir.RIGHT: "midright",
                  Dir.UP:    "midtop",
                  ( 1,  1):  "bottomright",
                  ( 1, -1):  "topright",
                  (-1,  1):  "bottomleft",
                  (-1, -1):  "topleft",}

    # Resource to get the player size
    ref = "player_1"
    
    def init(self, pid):
        """Initialize the player."""
        # Attributes
        self.id = pid
        self.border = self.parent.border
        self.resource = self.control.resource
        # Player rectangle
        self.size = self.resource.image.get(self.ref)[0].get_size()
        self.rect = Rect((0,0), self.size)
        if pid == 1:
            self.rect.bottomleft = self.border.rect.bottomleft
        else:
            self.rect.bottomright = self.border.rect.bottomright
        # Player state
        self.speed = self.remainder = xytuple(0.0,0.0)
        self.control_dir = Dir.NONE
        self.pos = Dir.DOWN
        self.fixed = True
        self.loading = False
        self.ko = False
        self.loading_speed = self.init_speed
        # Animation timer
        self.timer = Timer(self, stop=self.period, periodic=True)
        self.timer.start()
        # Debug
        if self.display_hitbox:
            RectModel(self, "head", Color("red"))
            RectModel(self, "body", Color("green"))
            RectModel(self, "legs", Color("blue"))

    @property
    def delta_tuple(self):
        """Delta time as an xytuple."""
        return xytuple(self.delta, self.delta)

    def set_ko(self):
        """Knock the player out."""
        self.ko = True
        self.fixed = False

    def load(self):
        """Start loading the jump."""
        self.loading = True

    def jump(self):
        """Make the player jump."""
        # Check conditions
        if self.fixed and not self.ko:
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
        """Handle wall collisions."""
        collide_dct = dict(self.collide_dct.items())
        # Loop over changes
        while not self.border.rect.contains(self.rect):
            self.fixed = True
            dct = {}
            # Test against the 4 directions.
            for direc, attr in collide_dct.items():
                rect = self.rect.copy()
                value = getattr(self.border.rect, attr)
                setattr(rect, attr, value)
                distance = abs(xytuple(*rect.topleft) - self.rect.topleft)
                dct[distance] = rect, direc, attr
            # Aply the smallest change
            self.rect, self.pos, _ = dct[min(dct)]
            del collide_dct[self.pos]
        # Do not grab the wall when KO
        if self.ko and self.pos != Dir.DOWN:
            self.fixed = False

    @property
    def loading_ratio(self):
        """Loading ratio between 0 and 1."""
        res = float(self.loading_speed - self.init_speed)
        return res / (self.max_loading_speed - self.init_speed)

    @property
    def current_dir(self):
        """Current direction with x and y in (-1, 0, 1)."""
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
        """Compute a hitbox inside the player in a given direction."""
        size = xytuple(*self.size) / (2,2)
        attr = self.attr_dct[direction]
        rect = Rect((0,0), size)
        value = getattr(self.rect, attr)
        setattr(rect, attr, value)
        return rect

    @property
    def head(self):
        """Head hitbox."""
        if self.ko:
            return Rect(0,0,0,0)
        if self.fixed:       
            return self.get_rect_from_dir(self.pos * (-1,-1))
        return self.get_rect_from_dir(self.current_dir * (-1,-1))

    @property
    def body(self):
        """Body hitbox."""
        if self.ko:
            return Rect(0,0,0,0)
        return self.get_rect_from_dir(Dir.NONE)

    @property
    def legs(self):
        """Legs hitbox."""
        if self.ko:
            return Rect(0,0,0,0)
        if self.fixed:       
            return self.get_rect_from_dir(self.pos)
        return self.get_rect_from_dir(self.current_dir)

    def update(self):
        """Update the player state."""
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
