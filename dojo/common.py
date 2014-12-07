"""Provide common functions."""

# Imports
import pygame
from mvctools import xytuple


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

