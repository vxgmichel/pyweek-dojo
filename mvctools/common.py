"""Module with useful classes and functions."""

# Imports
import operator
from math import ceil
from functools import wraps
from collections import namedtuple, defaultdict
from pygame import Color


# XY namedtuple
class xytuple(namedtuple("xytuple",("x","y"))):
    """Tuple for x,y coordinates and their transformations.

    This class supports the following operators:
     - addition and inplace addition (+, +=)
     - substraction and inplace substraction (-, -=)
     - multiplication and inplace multiplication (* , * =)
     - division and inplace division (/, /=)

    These are all term-to-term operations.
    Hence, the argument has two be a two-elements iterable.
    They all return an xytuple.

    Also, the absolute value operation is supported (abs).
    It returned a float corrsponding to the norm of the coordinates.

    To apply a specific function on both coordinates, use the method map.
    It returns an xytuple.
    """

    def __new__(cls, x, y=None):
        """Create a new xytuple."""
        if y is None: x, y = x
        return super(xytuple, cls).__new__(cls, x, y)

    __add__ = __iadd__ = lambda self, it: xytuple(*map(operator.add, self, it))
    __add__.__doc__ = """Add a 2-elements iterable and return an xytuple.
                      """
    __sub__ = __isub__ = lambda self, it: xytuple(*map(operator.sub, self, it))
    __sub__.__doc__ = """Substract a 2-elements iterable and return an xytuple.
                      """
    __mul__ = __imul__ = lambda self, it: xytuple(*map(operator.mul, self, it))
    __mul__.__doc__ = """Product by a 2-elements iterable and return an xytuple.
                      """
    __div__ = __idiv__ = lambda self, it: xytuple(*map(operator.div, self, it))
    __div__.__doc__ = """Divide by a 2-elements iterable and return an xytuple.
                      """
    __neg__ = lambda self: self * (-1,-1)
    __neg__.__doc__ = """Return the additive inverse of an xytuple.
                      """
    __abs__ = lambda self: abs(complex(*self))
    __abs__.__doc__ = """Return a float, the norm of the coordinates.
                      """

    def map(self, func):
        """Map the coordinates with the given function a return an xytuple."""
        return xytuple(*map(func, self))


# Direction enumeration
class Dir:
    NONE = xytuple(0,0)
    UP = xytuple(0,-1)
    DOWN = xytuple(0,+1)
    LEFT = xytuple(-1,0)
    RIGHT = xytuple(+1,0)
    UPLEFT = UP + LEFT
    UPRIGHT = UP + RIGHT
    DOWNLEFT = DOWN + LEFT
    DOWNRIGHT = DOWN + RIGHT


# Cursored list
class cursoredlist(list):
    """Enhanced list with a cursor attribute

    Args:
        iterator (any iterable): Iterator to build the list from
        pos (int): Initial cursor value (default is 0)
    """

    def __init__(self, iterator, cursor=0):
        """Inititalize the cursor."""
        list.__init__(self, iterator)
        self.cursor = cursor

    def get(self, default=None):
        """Get the current object."""
        if len(self):
            self.cursor %= len(self)
        try:
            return self[self.cursor]
        except IndexError:
            return default

    def inc(self, inc):
        """Increment the cursor and return the new current object.

        Args:
            inc (int): Number of incrementation of the cursor
        """
        self.cursor += inc
        return self.get()

    def dec(self, dec):
        """Decrement the cursor and return the new current object.

        Args:
            dec (int): Number of decrementation of the cursor
        """
        self.cursor -= dec
        return self.get()

    def set(self, index):
        """Set the cursor to an arbitrary index value."""
        if len(self):
            self.cursor = index % len(self)


# Scale rectangles function
def scale_rects(rects, source_size, dest_size):
    if not all(source_size):
        return
    ratio = xytuple(*dest_size).map(float)/source_size
    for rect in rects:
        topleft = (ratio * rect.topleft).map(int)
        bottomright = (ratio * rect.bottomright).map(ceil)
        rect.topleft, rect.size = topleft, bottomright - topleft
    return rects


# Cache dictionary
class cachedict(defaultdict):

    def __missing__(self, key):
        if isinstance(key, tuple):
            self[key] = self.default_factory(*key)
        else:
            self[key] = self.default_factory(index)
        return self[key]


# Cache decorator
def cache(func, static=False):
    dct = {}
    @wraps(func)
    def wrapper(*args):
        if args not in dct:
            dct[args] = func(*args[static:])
        return dct[args]
    return wrapper


# From parent decorator
def from_parent(lst):
    # Getter generator
    gen_getter = lambda attr: lambda self: getattr(self.parent, attr)
    # Decorator
    def decorator(cls):
        # Loop over attributes
        for attr in lst:
            # Set property
            setattr(cls, attr, property(gen_getter(attr)))
        return cls
    # Return
    return decorator


# Color class
class Color(Color):
    """TODO: Enhanced version of pygame.Color."""
    pass

