pyweek-dojo
===========

A minimalistic versus fighting game (and a Pyweek 19 entry).

![Screenshot](/resource/image/screenshot.png?raw=true "ScreenShot")

In one dojo, with one life, so one hit causes one win.
The gameplay is based on the fact that you can grab the walls
and ceiling of the room to jump on your opponent.

## Requirement

 - Python 2.7
 - Pygame 1.9

## Run locally

    $ python Dojo.py # Or
    $ python -m dojo

## Installation

    $ python setup.py install

## Build executable

    $ pyinstaller Dojo.spec

## Gameplay

 - Since it's a versus fighting game, you need to be two players.
 - The characters can't walk, run or hit. Only jump.
 - It is possible to jump higher by keeping the jump button pressed.
 - It is possible for a player to let himself down by pressing jump without direction.
 - The game switches to slow motion when players are close to hit each other.
 - A player is considered KO when he's hit by the legs of the attacking player.
 - When players jump onto each other, they bounce.
 - To start a new match, reset by pressing "U".
 - Counters on the wall keep track of the score.
 - Controllers are supported (reset to detect new controllers).

## Controls

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

**General:**
  - Reset : U
  - Quit : Escape

## Settings

One can change the the screen size, the frame rate or switch
to fullscreen mode by using the command line interface:

    $ python Dojo.py -h # To display the complete description
	usage: Dojo.py [-h] [--version] [--fps FPS] [--fullscreen] [--size SIZE]
	[...]
	$ python Dojo.py --size 800x600 --fps 50 --fullscreen # Example

Here is the argument list:

  - **-h, --help**:   show this help message and exit
  - **--version**:    show program's version number and exit
  - **--fps FPS**:    frame rate in frames per second (default is 60)
  - **--fullscreen**: enable fullscreen mode (inactive when omitted)
  - **--size SIZE**:  size of the screen (default is 1280x720)

Note: The window size is completely decoupled from the game size
and the frame rate doesn't affect the actual speed of the game.

## MVC Tools

The game is based on [pygame-mvctools](https://github.com/vxgmichel/pygame-mvctools),
a library for writing games using the model-view-controller design pattern.

## Repository

These sources are available on [gitbub]
(https://github.com/vxgmichel/pyweek-dojo).

## Windows executable

A windows executable is available on [sourceforge]
(https://sourceforge.net/projects/pyweek-dojo/files/latest/download).

## License

pyweek-dojo is licensed under the [GPLv3](http://www.gnu.org/licenses/gpl-3.0-standalone.html)

## Author

Vincent Michel
