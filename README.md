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
 - If they touch a wall or the ceiling, they'll automatically grab it.
 - In a given position, 4 directions are available:
    - Jump at 0 degree
    - Jump at - 45 degrees
    - Jump at + 45 degrees
    - Or let yourself down
 - It is possible to jump higher by keeping the jump button pressed.
 - A player is considered KO when he's hit by the legs of the attacking player.
 - When players jump onto each other, they bounce.
 - To start a new match, reset by pressing "R".
 - Counters on the wall keep track of the score.
 - Controllers are supported (reset to detect new controllers).
	
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
  - Quit : Escape
  
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