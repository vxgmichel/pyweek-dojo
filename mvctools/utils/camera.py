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
        diag = xytuple(*rect.topleft) - rect.bottomright
        self.base_length = abs(diag)
        self.camera_speed = speed

    def reset_camera(self, force=False):
        self.target_rect = self.base_rect
        if force:
            self.camera_rect = self.base_rect

    def set_camera(self, rect):
        self.target_rect = Rect(rect)

    def update(self):
        print self.target_rect, self.camera_rect
        if self.camera_speed is None:
            self.camera_rect = Rect(self.target_rect)
            return
        dct = {}
        step = float(self.base_length * self.delta * self.camera_speed)
        for attr in ("w", "h", "centerx", "centery"):
            target = getattr(self.target_rect, attr)
            current = getattr(self.camera_rect, attr)
            delta = float(target) - current
            distance = abs(delta)
            if distance <= step:
                dct[attr] = target
            else:
               delta *= step/distance
               dct[attr] = current + delta
        self.camera_rect = Rect(0, 0, dct["w"], dct["h"])
        self.camera_rect.center = dct["centerx"], dct["centery"] 
        
##    def update(self):
##        print self.target_rect, self.camera_rect
##        if self.camera_speed is None:
##            self.camera_rect = Rect(self.target_rect)
##            return
##        dct = {}
##        step = float(self.base_length * self.delta * self.camera_speed)
##        for attr in ("topleft", "bottomright"):
##            target = getattr(self.target_rect, attr)
##            current = getattr(self.camera_rect, attr)
##            delta = xytuple(*target).map(float) - current
##            distance = abs(delta)
##            if distance <= step:
##                dct[attr] = xytuple(*target)
##            else:
##               delta *= (step/distance,) * 2
##               print attr, delta
##               dct[attr] = delta + current
##        self.camera_rect.size = dct["bottomright"] - dct["topleft"]
##        self.camera_rect.topleft = dct["topleft"]
##        
        
        

class CameraSprite(ViewSprite):

    @property
    def view_cls(self):
        return self.parent.view_cls

    @property
    def size(self):
        return self.parent.size

    def get_rect(self):
        return self.image.get_rect()

    def transform(self, screen, dirty):
        if self.model.camera_rect != screen.get_rect():
            dirty[:] = []
            cropped = Surface(self.model.camera_rect.size).convert_alpha()
            cropped.blit(screen, (0, 0), self.model.camera_rect)
            return ViewSprite.transform(self, cropped, dirty)
        elif not dirty or not dirty[0].unionall(dirty[1:]):
            return self.image
        return ViewSprite.transform(self, screen, dirty)

    @property
    def screen_size(self):
        return self.view.screen.get_size()
        

class CameraView(BaseView):

    view_cls = BaseView

    def init(self):
        self.camera = CameraSprite(self)


    
