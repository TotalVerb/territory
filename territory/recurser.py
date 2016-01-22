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

import random


class Recurser:
    def __init__(self, board):
        self.board = board

    def count_dumps_on_island(self, x, y):
        dumps_coord_list = []
        player = self.board.data[x, y]
        # Crawl island from (x, y)
        land_area = self.crawl(x, y, [player])
        # Let's iterate through crawled places
        for coordinate in land_area:
            # Check if current coordinate has a dump
            # (data can take the coordinate-string)
            actor = self.board.actor_at(coordinate)
            if actor and actor.dump:
                assert actor.side == player
                dumps_coord_list.append(coordinate)
        return [dumps_coord_list, land_area]

    def recurse_new_random_coord_for_dump_on_island(self, x, y):
        land_area = self.crawl(x, y, [self.board.data[x, y]])
        # Check if island has area to afford dump
        if len(land_area) > 1:
            # It has enough area
            return [random.choice(list(land_area)), list(land_area)]
        else:
            # Not enough area, be careful with handling the None
            return None

    def find_land(self):
        """Find a square with land."""
        for x in range(self.board.width):
            for y in range(self.board.height):
                if self.board.data[x, y] > 0:
                    return x, y

    def iscontiguous(self):
        """Return true if every land is connected to every other."""

        # Check if there's at least one land. No point handling vacuous truth.
        land_area = self.board.count_world_area()
        assert land_area > 0

        x, y = self.find_land()
        return len(self.crawl(x, y, [1, 2, 3, 4, 5, 6])) == land_area

    def count_owned_islands(self, turn=None):
        """Count the number of islands controlled by the given player."""
        turn = turn or self.board.turn
        acc = 0
        seen = set()
        for x in range(self.board.width):
            for y in range(self.board.height):
                if (x, y) not in seen and self.board.data[x, y] == turn:
                    seen |= self.crawl(x, y, [self.board.turn])
                    acc += 1
        return acc

    def get_island_border_lands(self, x, y):
        land_area_set = set()
        island_owner = self.board.data[x, y]
        self.crawl(x, y, [island_owner], land_area_set)
        border_area_set = set()
        for xy in land_area_set:
            x1, y1 = xy
            for nx, ny in self.board.neighbours(x1, y1):
                if self.board.isvalid(nx, ny) \
                        and self.board.data[nx, ny] != island_owner \
                        and self.board.data[nx, ny] != 0:
                    # This works because set can't have duplicates
                    border_area_set.add((nx, ny))
        return border_area_set

    def island_size(self, x, y):
        """Count the amount of land of the specified island."""
        return len(self.crawl(x, y, [self.board.data[x, y]]))

    def crawl(self, x, y, find_list, crawled=None):
        """
        x,y -> coordinates to start "crawling"
        recursion_set -> set to hold already "crawled" coordinates
        find_list -> list of players whose lands are to be searched
        """
        crawled = crawled if crawled is not None else set()
        if self.board.isvalid(x, y) and \
                        self.board.data[x, y] in find_list and \
                        (x, y) not in crawled:
            crawled.add((x, y))
            # Crawl neighbours
            for nx, ny in self.board.neighbours(x, y):
                self.crawl(nx, ny, find_list, crawled)
        return crawled  # places crawled
