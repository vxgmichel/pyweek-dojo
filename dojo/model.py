"""Contain the model for the main game state."""

# Imports
from pygame import Rect, Color
from mvctools import BaseModel, xytuple, Timer, property_from_gamedata
from mvctools.utils.camera import CameraModel
from dojo.common import Dir

# Dojo model
class DojoModel(CameraModel):
    """Dojo model for the main game state."""
    
    # Resource to get the model size
    ref = "room"

    # Camera speed
    speed = 300 # pixel / s

    def init(self):
        """Initialize camera."""
        self.resource = self.control.resource
        self.size = self.resource.image.get(self.ref).get_size()
        self.room_rect = Rect((0,0), self.size)
        self.init_camera(self.room_rect, self.speed)
        self.room = RoomModel(self, self.room_rect)

    def register(self, *args, **kwargs):
        # Forward actions
        return self.room.register(*args, **kwargs)

        
# Room model
class RoomModel(BaseModel):
    """Dojo model for the main game state."""

    # Damping when two players collide
    damping = 0.8

    # Title
    text = "Dojo"

    def init(self, room_rect):
        """Initialize players and borders."""
        self.rect = room_rect
        self.size = self.rect.size
        self.border = BorderModel(self)
        self.players = {i:PlayerModel(self, i) for i in (1,2)}
        self.colliding = False

    @property_from_gamedata("score_dct")
    def score_dct(self):
        return {i:0 for i in (1,2)}
    
    def register_activate(self, player, down):
        """Register a jump from the controller."""
        player = self.players[player]
        player.load() if down else player.jump()

    def register_reset(self):
        """Register a reset from the controller."""
        self.control.register_next_state(type(self.state))
        return True

    def register_escape(self):
        """Register an escape from the controller."""
        return True
            
    def register_dir(self, player, direction):
        """Register a direction change from the controller."""
        self.players[player].register_dir(direction)

    def update_speed(self):
        # Settings
        threshold = 16
        slow = 0.2
        # Get distance
        lst = [float("inf")]
        for i in (1,2):
            j = 2 if i==1 else 1
            pos_1 = xytuple(*self.players[i].legs.center)
            if not any(pos_1):
                continue
            pos_2 = xytuple(*self.players[j].head.center)
            pos_3 = xytuple(*self.players[j].body.center)
            lst.append(abs(pos_1-pos_2))
            lst.append(abs(pos_1-pos_3))
        # Set speed
        if min(lst) > float(threshold):
            self.time_speed = 1.0
            self.parent.reset_camera()
        else:
            self.time_speed = slow
            area = self.players[1].rect.union(self.players[2].rect)
            if self.parent.is_camera_set and \
               self.parent.target_rect.contains(area.clamp(self.rect)):
                return
            target_ratio = float(self.rect.w)/self.rect.h
            actual_ratio = float(area.w)/area.h
            center = area.center
            if target_ratio > actual_ratio:
                area.w = round(area.h * 1.2 * target_ratio)
                area.h = round(area.h * 1.2)
            else:
                area.h = round(area.h * 1.2)
                area.h = round(area.w * 1.2 / target_ratio)
            area.center = center
            self.parent.set_camera(area.clamp(self.rect))
            

    def update(self):
        """Detect collision between the 2 players."""
        self.update_speed()
        hit = {}
        for i in (1,2):
            j = 2 if i==1 else 1
            lst = [self.players[j].legs, self.players[j].body, self.players[j].head]
            index = self.players[i].legs.collidelist(lst)
            hit[i] = index > 0
            tie = not index
        collide = tie or any(hit.values())
        if collide and not self.colliding:
            for i in (1,2):
                j = 2 if i==1 else 1
                if hit[i] and not hit[j]:
                    self.score_dct[i] += 1
                if hit[i]:
                    self.players[j].set_ko()
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
    init_speed = 250         # pixel/s
    max_loading_speed = 1000 # pixel/s

    # Animation
    period = 2.0         # s
    pre_jump = 0.25      # s
    load_factor_min = 5  # period-1
    load_factor_max = 10 # period-1

    # Hitbox
    hitbox_ratio = 0.25

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
        self.save_dir = Dir.NONE
        self.pos = Dir.DOWN
        self.fixed = True
        self.ko = False
        # Animation timer
        self.timer = Timer(self,
                           stop=self.period,
                           periodic=True).start()
        # Loading timer
        self.loading_timer = Timer(self,
                                   start=self.init_speed,
                                   stop=self.max_loading_speed)
        # Delay timer
        self.delay_timer = Timer(self,
                                 stop=self.pre_jump,
                                 callback=self.delay_callback)
        # Debug
        if self.control.settings.display_hitbox:
            RectModel(self, "head", Color("red"))
            RectModel(self, "body", Color("green"))
            RectModel(self, "legs", Color("blue"))

    def register_dir(self, direction):
        if any(direction):
            self.save_dir = direction
        self.control_dir = direction

    @property
    def delta_tuple(self):
        """Delta time as an xytuple."""
        return xytuple(self.delta, self.delta)

    @property
    def loading(self):
        return self.loading_timer.is_set or not self.loading_timer.is_paused

    @property
    def loading_speed(self):
        return self.loading_timer.get()
    
    def set_ko(self):
        """Knock the player out."""
        self.ko = True
        self.fixed = False

    def load(self):
        self.delay_timer.reset().start()
        self.timer.set(self.period*0.9)

    def delay_callback(self, timer):
        """Start loading the jump."""
        self.loading_timer.reset().start(self.load_speed)
        self.timer.reset().start()

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
                self.save_dir = Dir.NONE
                self.pos = Dir.NONE
                self.fixed = False
        # Reset loading
        self.delay_timer.reset()
        self.loading_timer.reset()
        # Reset animation
        self.timer.reset().start()

    def update_collision(self):
        """Handle wall collisions."""
        collide_dct = dict(self.collide_dct.items())
        # Loop over changes
        while not self.border.rect.contains(self.rect):
            self.fixed = True
            self.save_dir = self.control_dir
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
            if not any(self.save_dir) or \
               sum(self.save_dir*self.pos) > 0:
                return xytuple(0,0)
            current_dir = self.save_dir - self.pos
            sign = lambda arg: cmp(arg, 0)
            return current_dir.map(sign)
        # Dynamic case
        lst = []
        for x in range(-1,2):
            for y in range(-1,2):
                if x or y:
                    norm = xytuple(x,y).map(float)
                    norm /= (abs(norm),)*2
                    value = abs(self.speed-norm)
                    lst.append((value, x, y))
        _, x, y = min(lst)
        return xytuple(x,y)

    def get_rect_from_dir(self, direction):
        """Compute a hitbox inside the player in a given direction."""
        size = xytuple(*self.size) * ((self.hitbox_ratio,)*2)
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
        if self.ko or self.fixed:
            return Rect(0,0,0,0)
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
        # Get step
        step = self.delta_tuple * self.speed
        step += self.remainder
        intstep = step.map(round)
        self.remainder = step - intstep
        # Update rect
        self.rect.move_ip(intstep)
        self.update_collision()
        # Update timer
        if self.loading:
            delta = self.load_factor_max - self.load_factor_min
            ratio = self.load_factor_min + self.loading_ratio * delta
            self.timer.start(ratio)
