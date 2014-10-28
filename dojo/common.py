from mvctools import xytuple

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

DIR_TO_ATTR = {Dir.NONE: "center",
               Dir.UP: "midtop",
               Dir.DOWN: "midbottom",
               Dir.LEFT: "midleft",
               Dir.RIGHT: "midright",
               Dir.UPLEFT: "topleft",
               Dir.UPRIGHT: "topright",
               Dir.DOWNLEFT: "bottomleft",
               Dir.DOWNRIGHT: "bottomright",}
    
