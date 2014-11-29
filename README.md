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

    $ python Dojo.py 
    # Or
    $ python -m dojo

## Installation

    $ python setup.py install

## Build executable

    $ pyinstaller Dojo.spec
	
## Gameplay

 - Since it's a versus fighting game, you need to be two players.
 - The characters can't walk, run or hit. Only jump.
 - The control direction when the jump key is released fixes the jump direction
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

It is possible to change the size, fps and fullscreen settings by editing the values 
in the main() function (`dojo/__init__.py`):

 - **dojo.settings.fullscreen**: Set it to True for fullscreen mode, default is False.
 - **dojo.settings.size**: The window size is completely decoupled from the game size. 
 - **dojo.settings.fps**: The actual speed of the game is not affected by this value.

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
