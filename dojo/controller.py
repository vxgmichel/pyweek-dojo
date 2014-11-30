"""Contain the controller for the main game state."""

# Imports
from mvctools.utils import TwoPlayersController, PlayerAction


# Dojo controller
class DojoController(TwoPlayersController):
    """Main state controller, based on TwoPLayersCOntroller.

    ACTIVATE is used for jumping, START is use for reset.
    BACK and SELECT actions are not used.
    """

    # Allow loading jump after a reset
    special_actions = [PlayerAction.ACTIVATE]

    # Add reset on Y button
    button_dct = dict(TwoPlayersController.button_dct)
    button_dct[3] = PlayerAction.START, False
