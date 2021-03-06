pyweek-dojo
===========

A minimalistic versus fighting game (and a Pyweek 19 entry).

![Screenshot](/resource/image/screenshot.png?raw=true "ScreenShot")

In one dojo, with one life, so one hit causes one win.
The gameplay is based on the fact that you can hold on to 
the walls and ceiling of the room to jump on your opponent.

Requirement
-----------

 - Python 2.7
 - Pygame 1.9

Run the game
------------

Run locally:

    $ python Dojo.py # Or
	$ python -m dojo

Or install it:

    $ python setup.py install
	$ Dojo

Gameplay
--------

 - Two modes are available: 1 player or 2 players
 - The characters can't walk, run or hit. Only jump.
 - It is possible to jump higher by keeping the jump button pressed.
 - It is possible for a player to let himself down by pressing jump without direction.
 - The game switches to bullet time when players are close to hit each other.
 - A player is considered KO when he's hit by the legs of the attacking player.
 - When players jump onto each other, they bounce.
 - To start a new match, reset by pressing "U".
 - Counters on the wall keep track of the score.
 - Controllers are supported (reset to detect new controllers).

Controls
--------

**Player 1:**
 - Move : RDFG
 - Jump : X or SPACE

**Player 2:**
 - Move : Arrows
 - Jump : P or ENTER (Keypad)

**Controller:**
 - Move : Hat or Axis
 - Jump : A (Button 0)
 - Reset: Y (Button 3)
 - Menu:  Start (Button 7)

**General:**
  - Rematch: U
  - Menu:    Escape

Settings
--------

One can change the screen size, scoring or switch to fullscreen in the 
settings screen. Alternatively, it is possible to use the command line 
interface:

    $ python Dojo.py -h # To display the complete description
	$ python Dojo.py --size 800x600 --fps 50 --fullscreen # Example

Here is the argument list:
  - **-h, --help**    : show this help message and exit
  - **--version**     : show program's version number and exit
  - **--fps FPS**     : frame rate in frames per second (default is 60)
  - **--fullscreen**  : enable fullscreen mode (inactive when omitted)
  - **--size SIZE**   : size of the screen (default is 1280x720)
  - **--scoring SCO** : scoring to win the game (default is 20)

The window size is completely decoupled from the game size
and the frame rate doesn't affect the actual speed.

MVC Tools
---------

The game is based on [pygame-mvctools]
(https://github.com/vxgmichel/pygame-mvctools),
a library for writing games using the model-view-controller design pattern.

The main purpose of this library is to easily design a game as a succession
of states. Each of these states owns its own model, view and controller for
which base classes are provided. Other high level features are available,
like resource handling and automatically updated sprites.

Repository
----------

These sources are available on [GitHub]
(https://github.com/vxgmichel/pyweek-dojo).

Windows executable
------------------

A windows executable can be found on [sourceforge]
(https://sourceforge.net/projects/pyweek-dojo/files/latest/download)
or built using `pyinstaller Dojo.spec`.

License
-------

pyweek-dojo is licensed under the [GPLv3]
(http://www.gnu.org/licenses/gpl-3.0-standalone.html).

Acknowledgement
---------------

Thanks to Johan Forsberg for the graphics.

Author
------

Vincent Michel
