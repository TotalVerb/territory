# ------------------------------------------------------------------------
#
#    This file is part of Territory.
#
#    Territory is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Territory is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Territory.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright Territory Development Team
#     <https://github.com/TotalVerb/territory>
#    Copyright Conquer Development Team (http://code.google.com/p/pyconquer/)
#
# ------------------------------------------------------------------------

"""Backend for the game, ideally handling logic but not display."""
from pathlib import Path

from territory.ruleset import DefaultRuleset


class Server:
    """A backend for the game."""
    def __init__(self, game_path: Path, ruleset: DefaultRuleset=None):
        """Create a new server.

        :param ruleset: The ruleset to use.
        """
        if ruleset is None:
            ruleset = DefaultRuleset()
        self.ruleset = ruleset

        self.game_path = game_path
