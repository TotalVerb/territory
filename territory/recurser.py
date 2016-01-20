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


_DEBUG = 0


class Recurser:
    def __init__(self, board):
        self.board = board
        self.recursed_land = set()
        self.recursed_own_land_count = 0

    def count_dumps_on_island(self, x, y):
        # Initialize set to be used in crawling
        land_area_rec = set()
        dumps_coord_list = []
        puolisko = self.board.data[x, y]
        # Crawl from (x,y), save crawling to land_area_rec and
        # crawl for playerid found in map data at (x,y)
        self.crawl(x, y, land_area_rec, [self.board.data[x, y]])
        # Lets iterate through crawled places
        for coordinate in land_area_rec:
            # Check if current coordinate has a dump
            # (data can take the coordinate-string)
            actorinssi = self.board.actor_at(coordinate)
            if actorinssi:
                if actorinssi.dump:
                    if actorinssi.side != puolisko:
                        self.board.actors.remove(actorinssi)
                    else:
                        dumps_coord_list.append(coordinate)
        return [dumps_coord_list, land_area_rec]

    def recurse_new_random_coord_for_dump_on_island(self, x, y):
        land_area_rec = set()
        self.crawl(x, y, land_area_rec, [self.board.data[x, y]])
        # Check if island has area to affor dump
        if len(land_area_rec) > 1:
            # It has enough area
            return [random.choice(list(land_area_rec)), list(land_area_rec)]
        else:
            # Not enough area, be careful with handling the None
            return None

    def is_the_whole_earth_connected(self, max_x=30):
        """Return true if every land is connected to every other."""
        # 1) Count land area 2) Recurse through one random land
        # 3) If recurse count == land area -> one big continent
        land_area = self.board.count_world_area()
        if _DEBUG > 1:
            print("World area: %d" % land_area)
        land_area_rec = set()

        for x in range(max_x):
            for y in range(14):
                if self.board.data[x, y] > 0:
                    break

        if self.board.data[x, y] == 0:
            return False

        self.crawl(x, y, land_area_rec, [1, 2, 3, 4, 5, 6])

        if len(land_area_rec) == land_area:
            return True
        else:
            return False

    def count_own_islands(self):
        # Count how many islands does player control
        laskuri = 0
        recursed_islands = set()
        for x in range(30):
            for y in range(14):
                if self.board.data[x, y] == self.board.turn:
                    if (x, y) not in recursed_islands:
                        self.recursed_own_land_count = 0
                        self.crawl(x, y, recursed_islands, [self.board.turn])
                        laskuri += 1
        return laskuri

    def get_island_border_lands(self, x, y):
        land_area_set = set()
        island_owner = self.board.data[x, y]
        self.crawl(x, y, land_area_set, [island_owner])
        border_area_set = set()
        for xy in land_area_set:
            x1, y1 = xy
            for nx, ny in self.board.neighbours(x1, y1):
                if self.board.validxy(nx, ny) \
                        and self.board.data[nx, ny] != island_owner \
                        and self.board.data[nx, ny] != 0:
                    # This works because set can't have duplicates
                    border_area_set.add((nx, ny))
        return border_area_set

    def recurse_own_island(self, x, y):
        # Count and recurse through own islands lands
        self.recursed_land.clear()
        self.recursed_own_land_count = 0
        self.crawl(x, y, self.recursed_land, [self.board.turn])
        return self.recursed_own_land_count

    def recurse_any_island(self, x, y):
        # Count and recurse through own islands lands
        xychosen = self.board.data[x, y]
        self.recursed_land.clear()
        self.recursed_own_land_count = 0
        self.crawl(x, y, self.recursed_land, [xychosen])
        return self.recursed_own_land_count

    def crawl(self, x, y, recursion_set, find_list):
        """
        x,y -> coordinates to start "crawling"
        recursion_set -> set to hold already "crawled" coordinates
        find_list -> list of players whose lands are to be searched
        """
        if self.board.validxy(x, y):
            # The current land in find_list?
            if self.board.data[x, y] in find_list:
                # Check whether the location has been crawled already
                if (x, y) not in recursion_set:
                    self.recursed_own_land_count += 1
                    recursion_set.add((x, y))
                    for nx, ny in self.board.neighbours(x, y):
                        # Crawl neighbours
                        self.crawl(nx, ny, recursion_set, find_list)
