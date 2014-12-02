
import pygame
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView
from mvctools.common import scale_rects


class NextStateException(Exception):
    pass

class TickContext(object):
    def __init__(self, state):
        self.state = state

    def __enter__(self):
        self.state.ticking = True

    def __exit__(self, error, value, traceback):
        self.state.ticking = False
        if error is NextStateException:
            return True


class BaseState(object):
    model_class = BaseModel
    controller_class = BaseController
    view_class = BaseView
    clock_class = pygame.time.Clock

    def __init__(self, control):
        self.control = control
        self.model = self.model_class(self)
        self.controller = self.controller_class(self, self.model)
        self.view = self.view_class(self, self.model)
        self.current_fps = self.control.settings.fps
        self.ticking = False

    def tick(self):
        mvc = self.controller, self.model, self.view
        with TickContext(self):
            return self.controller._update() or \
                   self.model._update() or \
                   self.update_view()
        return True

    def update_view(self):
        # Get the screens
        actual_screen = self.get_surface()
        screen, dirty = self.view._update()
        # Scale
        if actual_screen != screen:
            size = actual_screen.get_size()
            self.control.resource.scale(screen, size, actual_screen)
            scale_rects(dirty, screen.get_size(), size)
        # Update
        pygame.display.update(dirty)

    def get_surface(self):
        return pygame.display.get_surface()

    @property
    def delta(self):
        return 1.0 / self.current_fps

    def run(self):
        # Set current FPS
        self.current_fps = float(self.control.settings.fps)
        # Display FPS
        string = None
        if self.control.settings.display_fps:
            string = self.control.window_title + "   FPS = {:3}"
        # Create clock
        clock = self.clock_class()
        # Freeze current fps for the first two ticks
        if self.tick():
            return
        # Time control
        tick = self.control.settings.fps
        tick *= self.control.settings.debug_speed
        millisec = clock.tick(tick)
        # Profile
        if self.control.settings.profile:
            import cProfile, pstats
            profiler = cProfile.Profile()
            profiler.enable()
            clock.tick()
        # Loop over the state ticks
        while not self.tick():
            # Time control
            millisec = clock.tick(tick)
            # Update current FPS
            if millisec:
                self.current_fps = 1000.0/millisec
                self.current_fps /= self.control.settings.debug_speed
            # Update window caption
            rate = clock.get_fps()
            if rate and string:
                    caption = string.format(int(rate))
                    pygame.display.set_caption(caption)
        # Profile
        if self.control.settings.profile:
            profiler.disable()
            ps = pstats.Stats(profiler).sort_stats('tottime')
            ps.print_stats()

