from mvctools import xytuple

class Dir:
    UP = xytuple(0,-1)
    DOWN = xytuple(0,+1)
    LEFT = xytuple(-1,0)
    RIGHT = xytuple(+1,0)
    NONE = xytuple(0,0)
