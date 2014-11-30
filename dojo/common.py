from mvctools import xytuple, Dir
from pygame import PixelArray, Surface, BLEND_RGBA_MIN

DIR_TO_ATTR = {Dir.NONE: "center",
               Dir.UP: "midtop",
               Dir.DOWN: "midbottom",
               Dir.LEFT: "midleft",
               Dir.RIGHT: "midright",
               Dir.UPLEFT: "topleft",
               Dir.UPRIGHT: "topright",
               Dir.DOWNLEFT: "bottomleft",
               Dir.DOWNRIGHT: "bottomright",}


ALL_DIRS = [xytuple(x,y)
                for x in range(-1,2)
                    for y in range(-1,2)
                        if x or y]


ALL_NORMALIZED_DIRS = [d/(2*(abs(d),)) for d in ALL_DIRS]


def closest_dir(vector, normalized=False):
    dirs = ALL_NORMALIZED_DIRS if normalized else ALL_DIRS
    _, direc = min((abs(vector - direc), direc) for direc in dirs)
    if normalized:
        return direc.map(round).map(int)
    return direc


def generate_steps(old, new):
    lst = [old]
    while lst[-1].center != new.center:
        delta = xytuple(*new.center)-lst[-1].center
        step = closest_dir(delta)
        lst.append(lst[-1].move(step))
    return lst

def flatten(lst):
    if isinstance(lst, basestring):
        raise TypeError("basestring objects are not flattenable")
    for item in lst:
        try:
            for subitem in flatten(item):
                yield subitem
        except TypeError:
            yield item

def perfect_collide(rect1, img1, pos1, rect2, img2, pos2):
    rect = rect1.clip(rect2)
    if not rect: return False
    pos1, pos2 = xytuple(*pos1), xytuple(*pos2)
    surf = Surface(rect.size).convert_alpha()
    surf.blit(img1, (0,0), area=rect.move(-pos1),
              special_flags=BLEND_RGBA_MIN)
    surf.blit(img2, (0,0), area=rect.move(-pos2),
              special_flags=BLEND_RGBA_MIN)
    return any(flatten(PixelArray(surf)))

