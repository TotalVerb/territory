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

from territory import soundtrack


class Actor:
    """A soldier or dump."""

    def __init__(self, x, y, side, level=1, dump=False):
        self.x = x          # type: int
        self.y = y          # type: int
        self.side = side    # type: int
        self.level = level  # type: int
        self.dump = dump    # type: bool
        self.supplies = 0
        self.moved = False
        self.dead = False
        self.revenue = 0
        self.expenses = 0

    def die(self, sound=True):
        assert not self.dead
        self.dead = True
        if sound:
            soundtrack.play_sfx("die" if self.dump else "destroy")

    def upgrade(self, sound=False):
        assert self.level < 6
        assert not self.dump
        self.level += 1
        if sound:
            soundtrack.play_sfx("upgrade")
