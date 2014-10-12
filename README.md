pyweek-dojo
===========

A minimalistic versus fighting game (and a Pyweek 19 entry) 

![Screenshot](/resource/image/screenshot.png?raw=true "ScreenShot")

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

In a given position, 4 types of move are available:
 - Jump at 0 degree
 - Jump at - 45 degrees
 - Jump at + 45 degrees 
 - Let yourself down
 
Also note:
 - Jump can be loaded by keeping the jump button pressed
 - A player is considered KO he's hit by the legs of the attacking player.
 - When players jump onto each other, they bounce.
	
## Controls

**Player 1:**
 - Move : WASD 
 - Jump : Tab
 
**Player 2:**
 - Move : Arrows 
 - Jump : RightShift
 
**Controller:**
 - Move : Hat or Axis 
 - Jump : A (Button 0)
 - Reset: Y (Button 3)
 
**General:**
  - Reset : R
  
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