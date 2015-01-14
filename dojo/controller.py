"""Provide the controller for the main game state."""

# Imports
from mvctools.utils import TwoPlayersController, PlayerAction


# Dojo controller
class DojoController(TwoPlayersController):
    """Main state controller, based on TwoPLayersCOntroller.

    ACTIVATE is used for jumping, START is use for reset.
    BACK and SELECT actions are not used.
    """

    # Allow loading jump or picking a direction after a reset
    special_actions = [PlayerAction.DIR]

    # Remapping
    button_dct = dict(TwoPlayersController.button_dct)
    # Add reset on Y and Select buttons
    button_dct[3] = PlayerAction.START, False
    button_dct[6] = PlayerAction.START, False
    # Add escape on Start button
    button_dct[7] = PlayerAction.ESCAPE, False
