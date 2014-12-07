"""Provide common functions."""

# Imports
import pygame
from mvctools import xytuple


# Opacify function
def opacify_ip(surface, opacity):
    """Opacify a surface in place.

    The argument is a float between 0 and 1.
    """
    if opacity < 1:
        color = 255, 255, 255, int(255 * opacity)
        surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)


# Flash function
def flash(image, lighter=True, dark_offset=64, light_offset=32):
    """Create a lighter or darker copy of a given surface."""
    result = image.copy()
    delta = dark_offset if lighter else light_offset
    color = (delta, delta, delta*2, 0)
    flag = pygame.BLEND_RGBA_SUB if lighter else pygame.BLEND_RGBA_ADD
    result.fill(color, special_flags=flag)
    return result


# Flatten generator
def flatten(iterator):
    """Generator to flatten any iterable structure."""
    if isinstance(iterator, basestring):
        raise TypeError("basestring objects are not flattenable")
    for item in iterator:
        try:
            for subitem in flatten(item):
                yield subitem
        except TypeError:
            yield item


# Perfect collision function
def perfect_collide(rect1, img1, pos1, rect2, img2, pos2):
    """Perform a pixel-perfect collision test using transparency.

    It takes the inner rectangle, image and position for both elements.
    """
    rect = rect1.clip(rect2)
    if not rect:
        return False
    flag = pygame.BLEND_RGBA_MIN
    pos1, pos2 = xytuple(pos1), xytuple(pos2)
    surf = pygame.Surface(rect.size).convert_alpha()
    surf.blit(img1, (0,0), area=rect.move(-pos1), special_flags=flag)
    surf.blit(img2, (0,0), area=rect.move(-pos2), special_flags=flag)
    return any(flatten(pygame.PixelArray(surf)))

