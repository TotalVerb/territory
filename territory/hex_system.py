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

# This is the rectangular size of the hexagon tiles.
TILE_WIDTH = 38
TILE_HEIGHT = 41

# This is the distance in height between two rows.
ROW_HEIGHT = 31

# This value will be applied to all odd rows x value.
ODD_ROW_X_MOD = 19

# This is the size of the square grid that will help us convert pixel locations
# to hexagon map locations.
GRID_WIDTH = 38
GRID_HEIGHT = 31

# This is the modification tables for the square grid.
a1 = (-1, -1)
b1 = (0, 0)
c1 = (0, -1)

GRID_EVEN_ROWS = [
    [a1] * (18 - 2 * i) + [b1] * (2 + 4 * i) + [c1] * (18 - 2 * i)
    if i < 10 else [b1] * 38
    for i in range(31)
]

a2 = (-1, 0)
b2 = (0, -1)
c2 = (0, 0)

GRID_ODD_ROWS = [
    [a2] * (1 + 2 * i) + [b2] * (36 - 4 * i) + [c2] * (1 + 2 * i)
    if i < 10 else [a2] * 19 + [c2] * 19
    for i in range(31)
]
