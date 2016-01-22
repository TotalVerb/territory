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

# FIXME: This file is considered **too large**!
# As-is, maintenance is extremely difficult. This class has too many
# responsibilities.
# Some progress was made in Territory 0.2.2... but there's still a lot that can
# be done.

import json
import random
import time
from pathlib import Path

from territory import soundtrack
from territory.ai import AI
from territory.actor import Actor
from territory.player import Player
from territory.recurser import Recurser
from territory.server import Server
import territory.serializer as serializer

_DEBUG = 0

# Six direction neighbourhood matrix for even y coordinates
# (0, 2, 4, ..., n % 2 = 0)
HEX_EVEN_Y = (
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1)
)

# Six direction neighbourhood matrix for odd y coordinates
# (0, 2, 4, ..., n % 2 = 1)
HEX_ODD_Y = (
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, -1)
)


class CombatEngaged:
    """Combat has been engaged (move was not blocked)."""

    def __init__(self, success: bool):
        self.success = success


class GameBoard:
    """Class for game board and its logic."""

    @staticmethod
    def get_right_edm(y: int):
        # Selected right neighbourhood coordinate matrix
        if y % 2 == 1:
            return HEX_ODD_Y
        else:
            return HEX_EVEN_Y

    @classmethod
    def neighbours(cls, x: int, y: int):
        """Yield all neighbours of the given coordinates."""
        edm = cls.get_right_edm(y)
        for i in range(6):
            yield x + edm[i][0], y + edm[i][1]

    def __init__(self, server: Server, ruleset):
        self.server = server
        self.ruleset = ruleset

        # DATA is dictionary which has board pieces.
        # Values: playerid; 0 = Empty Space, 1-6 are player id:s
        self.data = {}
        self.width = 30
        self.height = 14

        # Pretty self-explanatory
        self.show_cpu_moves_with_lines = True

        # Fill the whole map with Empty Space.
        # Now the DATA has coordinate keys and values
        self.fill_map(0)

        # Instance of recurser engine
        self.rek = Recurser(self)

        # map_edit_info[0] = human player count in editable map
        # map_edit_info[1] = cpu player count in editable map
        # map_edit_info[2] = selected land in map editor
        self.map_edit_info = []
        self.map_edit_mode = False

        # Current turn
        self.turn = 1

        # Tuple that is used at sorting scorelist
        self.scores = ()

        # Actors set (set for optimization purposes) which holds every
        # instance of Actor-class (Soldiers and Dumps at the moment)
        self.actors = {Actor(0, 0, 0)}  # Make pycharm infer correct type
        self.actors.clear()

        # List of current players in a game
        self.playerlist = []

    def write_edit_map(self, path: Path):
        """Write edited map to file."""
        humans, computers = self.map_edit_info[0:2]
        with path.open('w') as file:
            json.dump({
                "players": ["human" for _ in range(humans)] +
                           ["ai" for _ in range(computers)],
                "data": serializer.to_string_dict(self.data),
                "width": self.width,
                "height": self.height
            }, file)

    def read_scenarios(self):
        # Get list of the scenario - folder's files and remove ".svn" - folder
        scenario_list = (self.server.game_path / "scenarios").iterdir()
        slc = [file for file in scenario_list
               if file.is_file()  # no directories
               and file.name[0] != "."  # no hidden files
               and file.name[-1] != "~"  # no backup files
               ]
        return slc

    def new_game(self, file=None, cpus=3, humans=3, cpu_names=None):
        """
        Prepare a new game.

        :param file: Filename for scenario; None for random generation
        :param cpus: CPU Player count in random generated map
        :param humans: Human Player count in random generated map
        """

        # Initial conditions
        self.turn = 1
        self.scores = ()
        self.playerlist = []
        self.map_edit_mode = False

        # If map is randomly generated, add players
        if file is None:
            for i in range(humans):
                self.playerlist.append(
                    Player("Player %d" % (i + 1), i + 1, None))
            for i in range(cpus):
                if cpu_names is None:
                    name = "CPU {}".format(i + 1)
                else:
                    name = "{} (cpu)".format(random.choice(cpu_names))
                    cpu_names.remove(name)
                self.playerlist.append(
                    Player(name, i + (humans + 1), AI(self)))

        # Clear data and actors from possible previous maps
        self.data = {}
        self.actors.clear()

        if file is None:
            # Generate random map
            self.generate_map(50)
        else:
            # Read a scenario
            self.load_map(self.server.game_path / "scenarios" / file)

        # Add resource dumps
        self.land_was_conquered()

        # Calculate income and expenses, and do changes for first players
        # supplies
        self.salary_time_to_dumps_by_turn([1], False)

        # Calculate everyone's supply, income and expenses
        self.salary_time_to_dumps_by_turn(self.get_player_id_list(), True)

    def get_player_id_list(self):
        # Make a player-id - list and return it
        return [it.id for it in self.playerlist]

    def count_world_area(self):
        """Count whole world's land count."""
        return sum(1 for v in self.data.values() if v > 0)

    def destroy_lonely_actors(self):
        """Destroy soldiers and dumps isolated onto one square."""
        # Let's iterate through the set copy as we may alter the original set
        for actor in self.actors.copy():
            # Only alive soldiers
            if not actor.dead:
                # If we find one (or more) friendly land next to soldier
                # or resource dump, actor will not be terminated.
                for nx, ny in self.neighbours(actor.x, actor.y):
                    if self.isvalid(nx, ny) and self.data[nx, ny] == actor.side:
                        # Adjacent friendly land: not isolated.
                        break
                else:
                    # Isolated and therefore discarded
                    self.actors.discard(actor)

    def isvalid(self, x: int, y: int):
        # Valid coordinate is a coordinate which is found in data
        return (x, y) in self.data

    def attempt_move(self, actor, x2, y2, only_simulation):
        """This function is called every time an actor tries to attack."""

        if actor.moved:
            # The soldier has already moved
            return

        # Blocked[0] -> Boolean value whether the target land is blocked
        # Blocked[1], Blocked[2] -> if target land is blocked, these
        # hold the coordinates for the reason of block.
        blocked = self.is_blocked(actor, x2, y2)

        # Is there an actor at target land?
        target = self.actor_at(x2, y2)  # type: Actor

        # The target is not blocked
        if not blocked[0]:

            # Check if it's a merger and not a conquest.
            # This occurs when the target actor is not hostile.
            if target and target.side == actor.side and not only_simulation:
                # Not blocked so don't bother checking actor level.
                # The target's move status does not change.
                target.level += actor.level
                actor.die(sound=False)
                self.actors.discard(actor)

                # Dump creation may be needed.
                self.land_was_conquered()
                return

            # Check for success (in lvl-6 vs lvl-6 battles the actor might
            # not succeed!
            if target and not target.dump:
                success = self.ruleset.takeover_attempt(actor, target)
            else:
                success = True

            # Both simulation and real attack makes changes to land owner
            if success:
                self.data[x2, y2] = actor.side

                # If simulating for AI, we don't want to make changes directly
                # to actors.
                if not only_simulation:
                    # Not simulating, not blocked, attacker conquered target
                    # land.
                    actor.x, actor.y = x2, y2
                    actor.moved = True
                    if target:
                        # If there was an actor (unit/dump) at target
                        # land, it is discarded (destroyed)
                        target.die()
                        self.actors.discard(target)

                    # Fix this to check one island (x2, y2) if dump creating
                    # needed
                    self.land_was_conquered()
            elif not only_simulation:
                # Unfortunately the target succeeds and actor dies.
                actor.die()
                self.actors.discard(actor)

                # One less actor -> maybe can fill dumps
                self.land_was_conquered()

            # Return result.
            return CombatEngaged(success)
        else:
            # Target is blocked. Return the reason for blocking.
            return blocked

    def get_player_by_side(self, side) -> Player:
        for player in self.playerlist:
            if player.id == side:
                return player

    def merge_dumps(self, dump_coords, island_area):
        """Merge dumps if the island has more than one dump.

        :param dump_coords: list of dump coordinates
        :param island_area: list of island's lands coordinates
        """

        # Summed supplies from islands dumps
        summed_supplies = 0

        # New dump goes where the biggest one was.
        biggest_dump = None
        biggest_dump_size = -float('inf')

        # List of dumps to be removed
        deletelist = []

        # If we have more than one dump on island and the island_area has items
        if len(dump_coords) > 1 and island_area:
            # Get player side (id) from first dump
            side = self.fetch_actor(dump_coords[0]).side

            # Iterate through dump coordinates
            for coord in dump_coords:
                # Get the dump's actor - instance
                current_dump = self.fetch_actor(coord)

                # We're told it's a dump...
                assert current_dump and current_dump.dump

                # Get random land coordinate of the island...
                # It does not matter which land of the island
                # Check if found actor's the same as island
                assert current_dump.side == self.data[island_area[0]]

                # We'll add the dumps supplies in the sum counter
                summed_supplies += current_dump.supplies

                # Is the dump bigger than biggest so far?
                if current_dump.supplies > biggest_dump_size:
                    biggest_dump = coord
                    biggest_dump_size = current_dump.supplies

                # The dump is going to be discarded
                deletelist.append(current_dump)

            # From actors remove every item in deletelist
            while deletelist:
                self.actors.discard(deletelist.pop())

            # Put new dump at biggest old dump.
            x11, y11 = biggest_dump

            # Create the dump
            new_dump = Actor(x11, y11, side, level=0, dump=True)
            new_dump.supplies = summed_supplies
            # Now the dump is registered
            self.actors.add(new_dump)

    def land_was_conquered(self):
        """Should be called when lands are conquered."""

        # Keep count of already searched lands
        searched = set()

        # Get list of current non-lost players
        alive_players = self.get_player_id_list()

        for xy, xy_pid in self.data.items():

            # Is the coordinate already crawled
            if xy in searched:
                continue

            # Fill Dumps only for existing and not lost players
            if xy_pid not in alive_players:
                continue

            x, y = xy

            # Not empty space
            if xy_pid > 0:
                # Ask if the island has Dump and get also crawled coordinates
                # search_dumps[0] -> list of coordinates for islands dump(s)
                # search_dumps[1] -> set of coordinates (islands every land coordinate)
                search_dumps = self.rek.count_dumps_on_island(x, y)

                # Update crawled coordinates
                searched.update(search_dumps[1])

                # Check if the island has not Dump yet, island has at least
                # 2 pieces of land and island is owned by existing player.
                if not search_dumps[0] and len(search_dumps[1]) > 1:

                    # Panic method to exit loop
                    for _ in range(100):
                        # Find a new place for dump:
                        #   - get a random legal coordinate from crawled island
                        coord = random.choice(list(search_dumps[1]))

                        if coord and not self.actor_at(coord):
                            # If a place was found for dump, we'll add
                            # a new dump in actors.
                            self.actors.add(
                                Actor(coord[0], coord[1], self.data[coord],
                                      dump=True))
                            break

                # More than one dump on island?
                elif len(search_dumps[0]) > 1:
                    # Then we'll merge dumps on the island
                    self.merge_dumps(search_dumps[0], list(search_dumps[1]))

    def fill_map(self, piece):
        self.data = {}
        for x in range(self.width):
            for y in range(self.height):
                self.data[x, y] = piece

    def actor_at(self, x, y=None):
        if y is None:
            x, y = x

        # Search actor - instances by coordinates
        for actor in self.actors:
            if actor.x == x and actor.y == y and not actor.dead:
                return actor

        # No actor found, return None
        return None

    def fetch_actor(self, xy) -> Actor:
        """Get the actor at the given coordinates.

        Raise an exception if no actor found."""
        x, y = xy
        for actor in self.actors:
            if actor.x == x and actor.y == y and not actor.dead:
                return actor
        raise ValueError('no actor found at {}'.format(xy))

    def fill_random_boxes(self, d, for_whom):
        """
        Fills a random box in the map
        for_who -> list of player ids (randomly selected for land owned)
        """
        # This just basically randoms coordinates and fills map
        if d > 0:
            while d > 0:
                x = random.randint(2, self.width - 1)
                y = random.randint(2, self.height - 1)
                for nx, ny in self.neighbours(x, y):
                    if self.isvalid(nx, ny):
                        pid = random.choice(for_whom)
                        self.data[nx, ny] = pid
                d -= 1

    def whole_map_situation_score(self, for_whom):
        return list(self.data.values()).count(for_whom)

    def is_blocked(self, actor, x, y):
        return self.ruleset.is_blocked(self, actor, x, y)

    def generate_map(self, minsize):
        """Generate a simple random map."""
        self.fill_map(0)
        while True:
            self.fill_random_boxes(1, [1, 2, 3, 4, 5, 6])
            if self.rek.iscontiguous() and self.count_world_area() >= minsize:
                break
        self.land_was_conquered()
        self.salary_time_to_dumps_by_turn(self.get_player_id_list(), True)

    def clean_dead(self):
        """Remove dead actors from the map."""
        for actor in self.actors.copy():
            if actor.dead:
                self.actors.discard(actor)

    def check_and_mark_if_someone_won(self):
        # If only one player has lost==False, he is winner
        no_losers = [z for z in self.playerlist if not z.lost]
        if len(no_losers) == 1:
            no_losers[0].won = True
            # calculate sound
            if not no_losers[0].ai_controller:
                soundtrack.play_sfx("victory")
            return True
        return False

    def load_map(self, map_path: Path):
        """Load a map from a file."""
        # TODO: Proper error handling.
        if self.map_edit_mode:
            self.map_edit_info = [0, 0, 1]

        with map_path.open('r') as file:
            data = json.load(file)
            self.width = data.get("width", self.width)
            self.height = data.get("height", self.height)
            self.data = serializer.from_string_dict(data["data"])
            for i, player in enumerate(data["players"]):
                if player == "human":
                    if not self.map_edit_mode:
                        self.playerlist.append(
                            Player("Player %d" % (i + 1), i + 1, None))
                    else:
                        self.map_edit_info[0] += 1
                elif player == "ai":
                    if not self.map_edit_mode:
                        self.playerlist.append(
                            Player("CPU {}".format(i + 1), i + 1, AI(self)))
                    else:
                        self.map_edit_info[1] += 1

    def has_anyone_lost_the_game(self):
        # Check if anyone has recently lost the game:
        #   - not marked as lost and has 0 dumps
        for candidate in self.playerlist:
            if self.count_dumps(
                    candidate.id) == 0 and not candidate.lost:
                candidate.lost = True

    def count_dumps(self, pid):
        return sum(1
                   for actor in self.actors
                   if actor.dump and actor.side == pid and not actor.dead)

    def cities(self, sides, safe=False):
        """Yield all cities of the given sides."""
        it = self.actors.copy() if safe else self.actors
        for actor in it:  # type: Actor
            if not actor.dead and actor.dump and actor.side in sides:
                yield actor

    def salary_time_to_dumps_by_turn(self, sides, just_do_math=False):
        """Calculate dumps' incomes, expenses and supplies.

        Kill soldiers without supplies.

        :param just_do_math: If true, only income and expenses are calculated.
        """
        dead = []
        coordinates = set()
        for city in self.cities(sides):
            possible_dead = []
            coordinates.clear()
            expense = 0
            self.rek.crawl(city.x, city.y, [city.side], coordinates)
            area = len(coordinates)
            for unit in self.actors:
                # Soldiers are costly for dump
                if (unit.x, unit.y) in coordinates and not unit.dump:
                    assert not unit.dead and unit.side == city.side
                    possible_dead.append(unit)
                    expense += self.ruleset.upkeep_costs[unit.level]
            city.revenue = area
            city.expenses = expense
            if not just_do_math:
                city.supplies += city.revenue - city.expenses
                if city.supplies < 0:
                    # Not enough supplies, islands soldiers are going
                    # to be terminated.
                    dead.extend(possible_dead)

                    # Prevent supplies from going below zero
                    # Terminating soldiers is enough of a punishment!
                    city.supplies = 0

        if not just_do_math:
            # Kill every soldier that doesn't have enough supplies
            while dead:
                tmp = dead.pop()

                # Remove the soldier from registered actors
                self.actors.discard(tmp)

    def draft_soldier(self, x, y, sound=True):
        """Soldier drafting function used by human and computer players."""

        # Valid coordinate?
        if not self.isvalid(x, y):
            return

        if self.data[x, y] != self.turn:
            return

        # Get the actor instance
        soldier_to_update = self.actor_at(x, y)

        # Check if actor was found
        if soldier_to_update:
            # Dump is not allowed
            if soldier_to_update.dump:
                return
            # We do not update level 6 soldiers
            if soldier_to_update.level == self.ruleset.max_level:
                return

        # Get the islands resource dump
        dumps = self.rek.count_dumps_on_island(x, y)

        # I hope we find just one dump ;)
        assert len(dumps[0]) == 1

        # Get the dump actor instance
        actor = self.actor_at(dumps[0][0])
        assert actor and actor.dump

        # Found the dump, check if it has supplies
        if actor.supplies >= self.ruleset.draft_cost:
            # It has, now minus draft cost
            actor.supplies -= self.ruleset.draft_cost
            if not soldier_to_update:
                # There wasn't a soldier to update, player draft a new
                ret = Actor(x, y, actor.side, level=1, dump=False)
                self.actors.add(ret)
            else:
                # The soldier is now updated
                soldier_to_update.upgrade(sound=sound)
                ret = soldier_to_update
            # Calculate dumps income and expends
            self.salary_time_to_dumps_by_turn([self.turn], True)
            return ret

    def end_turn(self):

        self.destroy_lonely_actors()
        self.has_anyone_lost_the_game()

        # Mark winner if found and get immediately "True"
        # if winner was found
        if self.check_and_mark_if_someone_won():
            # Someone won, break the recursion loop
            self.turn = 0
            self.data = {}
            self.actors.clear()
            self.fill_map(0)
            return

        for player in self.playerlist:
            if player.won:
                return

        self.turn += 1
        self.clean_dead()

        # Check if all players are scheduled already
        if len(self.playerlist) + 1 <= self.turn:
            # Show last player's moves
            time.sleep(0.2)
            self.turn = 1
            # Every actor's "moved" is reset
            for actor in self.actors:
                actor.moved = False

        # Update salaries and kill own unsupplied soldiers
        self.salary_time_to_dumps_by_turn([self.turn], False)
        # Update everyone's salaries
        self.salary_time_to_dumps_by_turn(self.get_player_id_list(), True)
