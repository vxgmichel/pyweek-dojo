from mvctools.sprite import ViewSprite
from mvctools.model import BaseModel
from mvctools.view import BaseView
from pygame import Surface, Rect
from mvctools import xytuple

class CameraModel(BaseModel):

    camera_speed = None

    def init_camera(self, rect, speed=None):
        self.base_rect = Rect(rect)
        self.camera_rect = Rect(rect)
        self.target_rect = Rect(rect)
        self.camera_speed = speed

    def reset_camera(self, force=False):
        self.target_rect = self.base_rect
        if force:
            self.camera_rect = self.base_rect

    def set_camera(self, rect):
        self.target_rect = Rect(rect)

    @property
    def is_camera_set(self):
        return not self.target_rect == self.base_rect

    def update(self):
        # No speed
        if self.camera_speed is None:
            self.camera_rect = Rect(self.target_rect)
            return
        # Get reference
        delta = {}
        for attr in ("top", "left", "bottom", "right"):
            target = getattr(self.target_rect, attr)
            current = getattr(self.camera_rect, attr)
            delta[attr] = float(target) - current
        ref = max(map(abs, delta.values()))
        step = float(self.delta * self.camera_speed)
        # Close enough
        if ref <= step:
            self.camera_rect = Rect(self.target_rect)
            return
        # Get new values
        ratio = step/ref
        dct = {}
        for attr in ("top", "left", "bottom", "right"):
            current = getattr(self.camera_rect, attr)
            dct[attr] = current + delta[attr] * ratio
        # Create rect
        for attr in dct:
            dct[attr] = round(dct[attr])
        size = dct["right"] - dct["left"], dct["bottom"] - dct["top"]
        topleft = dct["left"], dct["top"]
        self.camera_rect = Rect(topleft, size)        
        

class CameraSprite(ViewSprite):

    def init(self):
        ViewSprite.init(self)
        self.next_skip = False

    @property
    def view_cls(self):
        return self.parent.view_cls

    @property
    def size(self):
        return self.parent.size

    def get_rect(self):
        return self.image.get_rect()

    def transform(self, screen, dirty):
        # Crop the screen with the camera rectangle
        if self.model.camera_rect != screen.get_rect():
            dirty[:] = []
            self.next_skip = False
            cropped = Surface(self.model.camera_rect.size).convert_alpha()
            cropped.blit(screen, (0, 0), self.model.camera_rect)
            return ViewSprite.transform(self, cropped, dirty)
        # No update needed
        elif not dirty and self.next_skip:
            return self.image
        # Update needed
        elif not self.next_skip:
            dirty[:] = []
            self.set_dirty()
        # Update
        self.next_skip = True
        return ViewSprite.transform(self, screen, dirty)
        

class CameraView(BaseView):

    view_cls = BaseView

    def init(self):
        self.camera = CameraSprite(self)


    
