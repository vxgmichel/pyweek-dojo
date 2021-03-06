"""Provide the model for the main game state."""

# Imports
from pygame import Rect, Color
from mvctools import BaseModel, Dir, Timer, xytuple, from_gamedata, cursoredlist
from mvctools.utils import CameraModel, EntryModel, MenuModel
from dojo.common import perfect_collide
from dojo.pause import PauseState


# Dojo model
class DojoModel(CameraModel):
    """Dojo model for the main game state."""

    # Resource to get the model size
    ref = "room"

    # Camera speed
    speed = 300  # pixel / s

    # Display
    display_scores = True
    display_controls = False

    def init(self):
        """Initialize camera and create the room model."""
        self.resource = self.control.resource
        self.size = self.resource.image.get(self.ref).get_size()
        self.room_rect = Rect((0, 0), self.size)
        self.init_camera(self.room_rect, self.speed)
        self.room = RoomModel(self, self.room_rect)

    def pause(self, pause, callback):
        """Pause the game for a given time with a given callback."""
        self.room.time_speed, temp = 0, self.room.time_speed

        def target(timer):
            callback()
            self.room.time_speed = temp

        Timer(self, stop=pause, callback=target).start()

    def register(self, *args, **kwargs):
        """Forward actions to the room model."""
        return self.room.register(*args, **kwargs)


# Room model
class RoomModel(BaseModel):
    """Dojo model for the main game state."""

    # Damping when two players collide
    damping = 0.8

    # Pause when two players collide (with or without ko)
    pause_dct = {True: 1.0,
                 False: 0.5, }

    # Distance for slow motion
    threshold = 16

    # Speed ratio for slow motion
    slow_ratio = 0.2

    # Title
    text = "Dojo"

    def init(self, room_rect):
        """Initialize players and borders."""
        self.rect = room_rect
        self.size = self.rect.size
        self.border = BorderModel(self)
        self.players = {i: PlayerModel(self, i) for i in (1, 2)}
        self.colliding = False

    @from_gamedata
    def score_dct(self):
        """Get the score from gamedata."""
        return {i: 0 for i in (1, 2)}

    @property
    def display_controls(self):
        return self.parent.display_controls

    @property
    def display_scores(self):
        return self.parent.display_scores

    @property
    def gameover(self):
        return any(self.players[pid].ko for pid in (1, 2))

    @property
    def winner(self):
        if abs(self.score_dct[1] - self.score_dct[2]) < 2:
            return None
        pid = max(self.score_dct, key=self.score_dct.get)
        if self.score_dct[pid] >= self.control.settings.scoring:
            return pid

    def register_activate(self, down, player):
        """Register a jump from the controller."""
        player = self.players[player]
        if down:
            player.load()
        elif player.prepared:
            player.jump()

    def register_start(self, down):
        """Register a reset from the controller."""
        if down and self.gameover:
            state = type(self.state)
            if self.winner:
                state = self.control.first_state
            self.control.register_next_state(state)
            return True

    def register_escape(self, down):
        """Register an escape from the controller."""
        if down:
            self.control.push_current_state()
            self.control.register_next_state(PauseState)
            return True

    def register_dir(self, direction, player):
        """Register a direction change from the controller."""
        self.players[player].register_dir(direction)

    def post_update(self):
        """Decompose players trajectory into steps."""
        maxi = max(len(self.players[pid].steps) for pid in (1, 2)) - 1
        for i in range(maxi+1):
            for pid in (1, 2):
                length = len(self.players[pid].steps) - 1
                index = int(round(float(i*length)/maxi)) if maxi else 0
                self.players[pid].rect = self.players[pid].steps[index]
            if self.update_step():
                break

    def update_step(self):
        """Update everything for the current step."""
        return self.update_speed() or self.update_hit() \
            or self.update_collision()

    def update_speed(self):
        """Update camera and game speed."""
        # Get distance
        lst = [float("inf")]
        for i in (1, 2):
            j = 2 if i == 1 else 1
            pos_1 = xytuple(*self.players[i].legs.center)
            if not any(pos_1):
                continue
            pos_2 = xytuple(*self.players[j].head.center)
            pos_3 = xytuple(*self.players[j].body.center)
            lst.append(abs(pos_1-pos_2))
            lst.append(abs(pos_1-pos_3))
        # Reset speed and camera
        if not self.colliding and min(lst) > float(self.threshold):
            if self.time_speed:
                self.time_speed = 1.0
            self.parent.reset_camera()
            return
        # Set speed
        if self.time_speed:
            self.time_speed = self.slow_ratio
        # Set camera
        new_zoom = not self.parent.is_camera_set
        area = self.players[1].rect.union(self.players[2].rect)
        center = area.center
        area.h = max(area.h, self.rect.h/2)
        area.w = max(area.w, self.rect.w/2)
        area.center = center
        self.parent.set_camera(area.clamp(self.rect))
        # Break the update if new zoom detected
        return new_zoom

    def update_hit(self):
        """Test collision between players."""
        # Test ko
        if self.gameover:
            self.colliding = False
            return
        # Prepare collision function
        hit = {1: False, 2: False}
        collide = False
        img1, img2 = (self.players[pid].get_image() for pid in (1, 2))
        pos1, pos2 = (self.players[pid].rect.topleft for pid in (1, 2))
        collide_func = lambda r1, r2: perfect_collide(r1, img1, pos1,
                                                      r2, img2, pos2)
        # Test collision
        for i in (1, 2):
            j = 2 if i == 1 else 1
            if collide_func(self.players[i].legs, self.players[j].legs):
                collide = True
                break
            elif collide_func(self.players[i].legs, self.players[j].rect):
                hit[i] = collide = True
        # New collision
        if collide and not self.colliding:
            # Update
            for i, j in ((1, 2), (2, 1)):
                if hit[i] and not hit[j]:
                    self.score_dct[i] += 1
                    self.players[j].blinking_timer.start()
            # Pause
            self.colliding = True
            self.callback_data = hit
            pause = self.pause_dct[any(hit.values())]
            self.parent.pause(pause, self.callback)
            # Break the update
            return True
        # Update flag
        if not collide:
            self.colliding = False

    def update_collision(self):
        """Test collision against the wall."""
        for pid in (1, 2):
            self.players[pid].update_collision()

    def callback(self):
        """Callback to update the players when the pause is over."""
        # Bouncing
        p1, p2 = self.players[1], self.players[2]
        if p1.fixed:
            p2.speed *= (-self.damping,) * 2
        elif p2.fixed:
            p1.speed *= (-self.damping,) * 2
        else:
            p1.speed, p2.speed = p2.speed, p1.speed
        # Callback
        hit = self.callback_data
        for i, j in ((1, 2), (2, 1)):
            if hit[i]:
                self.players[j].set_ko()
                self.players[j].blinking_timer.reset()


# State entry model
class StateEntryModel(EntryModel):

    def init(self, pos, text, state=None):
        EntryModel.init(self, pos, text)
        self.state = state

    def activate(self):
        del self.parent.parent.score_dct
        self.control.register_next_state(self.state)
        return True

# State entry model
class SettingEntryModel(EntryModel):

    def init(self, pos, text, setting, values):
        self.pos = pos
        self.base_text = text
        self.setting = setting
        value = self.control.settings.setting_to_string(setting)
        self.values = cursoredlist(values)
        if value not in values:
            self.values.insert(0, value)
        self.values.set(self.values.index(value))

    @property
    def text(self):
        return self.base_text + " : " + self.values.get()

    def activate(self):
        self.apply_value()
        self.control.reload_state()

    def apply_value(self):
        setattr(self.control.settings, self.setting, self.values.get())

    def shift(self, shift):
        self.values.inc(shift)


# Title menu model
class TitleMenuModel(MenuModel):

    @property
    def entry_data(self):
        return {i: (StateEntryModel, name, state)
                for i, (name, state) in enumerate(self.state.entries)}


# Settings menu model
class SettingsMenuModel(MenuModel):

    @property
    def entry_data(self):
        return {0: (SettingEntryModel, "fullscreen",
                    "fullscreen", ['yes', 'no']),
                1: (SettingEntryModel, "size",
                    "size", ["640x360", "960x540", "1280x720", "1600x900"]),
                2: (SettingEntryModel, "scoring",
                    "scoring", ["10", "20", "30", "50", "80"]),
                3: (EntryModel, "apply", self.apply_callback),
                4: (EntryModel, "back ", self.back_callback)}

    def apply_callback(self):
        for entry in self.cursor:
            try:
                entry.apply_value()
            except AttributeError:
                pass
        self.control.reload_state()

    def back_callback(self):
        self.control.register_next_state(self.control.first_state)
        return True


# Border model
class BorderModel(BaseModel):
    """Border model. Useful to detect collision."""

    # Offset applied on the room size
    offset = -14, -15

    def init(self):
        """Compute the border rectangle."""
        self.rect = self.parent.rect.inflate(*self.offset)


# Rect model
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
    """Player model. Most of the game physics is implemented here."""

    # Physics
    air_friction = 0.5, 0.5   # s-1
    gravity = 0, 981          # pixel/s-2
    load_speed = 600          # pixel/s-2
    init_speed = 250          # pixel/s
    max_loading_speed = 1000  # pixel/s

    # Animation
    period = 2.0           # s
    pre_jump = 0.25        # s
    load_factor_min = 5    # period-1
    load_factor_max = 10   # period-1
    blinking_period = 0.2  # s

    # Hitbox
    hitbox_ratio = 0.33

    # Direction to Rect attributes for wall collision
    collide_dct = {Dir.DOWN: "bottom",
                   Dir.LEFT: "left",
                   Dir.RIGHT: "right",
                   Dir.UP: "top"}

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
        self.rect = Rect((0, 0), self.size)
        if pid == 1:
            self.rect.bottomleft = self.border.rect.bottomleft
        else:
            self.rect.bottomright = self.border.rect.bottomright
        # Player state
        self.speed = self.remainder = xytuple(0.0, 0.0)
        self.control_dir = Dir.NONE
        self.save_dir = Dir.NONE
        self.pos = Dir.DOWN
        self.fixed = True
        self.ko = False
        self.steps = [self.rect]
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
        # Dying timer
        self.blinking_timer = Timer(self.parent.parent,
                                    stop=self.blinking_period,
                                    periodic=True)
        # Debug
        if self.control.settings.debug_mode:
            RectModel(self, "head", Color("red"))
            RectModel(self, "body", Color("green"))
            RectModel(self, "legs", Color("blue"))

    def register_dir(self, direction):
        """Register a new direction from the controller."""
        if any(direction):
            self.save_dir = direction
        self.control_dir = direction

    @property
    def delta_tuple(self):
        """Delta time as an xytuple."""
        return xytuple(self.delta, self.delta)

    @property
    def colliding(self):
        """True when colliding with the other player, False otherwise."""
        return self.parent.colliding

    @property
    def loading(self):
        """True when the player is loading a jump, False otherwise."""
        return self.loading_timer.is_set or not self.loading_timer.is_paused

    @property
    def prepared(self):
        """True when the player is prepared a jump, False otherwise."""
        return self.loading or not self.delay_timer.is_paused

    @property
    def loading_speed(self):
        """The current loading speed value."""
        return self.loading_timer.get()

    def set_ko(self):
        """Knock the player out."""
        self.ko = True
        self.fixed = False

    def load(self):
        """Register a load action."""
        if self.colliding:
            return
        self.delay_timer.reset().start()
        self.timer.set(self.period*0.9)

    def delay_callback(self, timer):
        """Start loading the jump."""
        self.loading_timer.reset().start(self.load_speed)
        self.timer.reset().start()

    def jump(self):
        """Make the player jump."""
        if self.colliding:
            return
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
                return xytuple(0, 0)
            current_dir = self.save_dir - self.pos
            sign = lambda arg: cmp(arg, 0)
            return current_dir.map(sign)
        # Dynamic case
        return Dir.closest_dir(self.speed)

    def get_rect_from_dir(self, direction):
        """Compute a hitbox inside the player in a given direction."""
        size = xytuple(*self.size) * ((self.hitbox_ratio,)*2)
        attr = Dir.DIR_TO_ATTR[direction]
        rect = Rect((0, 0), size)
        value = getattr(self.rect, attr)
        setattr(rect, attr, value)
        return rect

    @property
    def head(self):
        """Head hitbox. Currently not used."""
        if self.ko:
            return Rect(0, 0, 0, 0)
        if self.fixed:
            return self.get_rect_from_dir(self.pos * (-1, -1))
        return self.get_rect_from_dir(self.current_dir * (-1, -1))

    @property
    def body(self):
        """Body hitbox. Currently not used."""
        if self.ko:
            return Rect(0, 0, 0, 0)
        return self.get_rect_from_dir(Dir.NONE)

    @property
    def legs(self):
        """Legs hitbox."""
        if self.ko or self.fixed:
            return Rect(0, 0, 0, 0)
        return self.get_rect_from_dir(self.current_dir)

    def update(self):
        """Update the player state."""
        # Get acc
        acc = -self.speed * self.air_friction
        acc += self.gravity
        # Update speed
        self.speed += self.delta_tuple * acc
        if self.fixed:
            self.speed *= 0, 0
        # Get step
        step = self.delta_tuple * self.speed
        step += self.remainder
        intstep = step.map(round)
        self.remainder = step - intstep
        # Register steps
        args = Rect(self.rect), self.rect.move(intstep)
        self.steps = list(Dir.generate_rects(*args))
        # Update timer
        if self.loading:
            delta = self.load_factor_max - self.load_factor_min
            ratio = self.load_factor_min + self.loading_ratio * delta
            self.timer.start(ratio)
