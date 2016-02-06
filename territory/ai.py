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
from territory.actor import Actor

AI_RECURSION_DEPTH = 10


class AI:
    def __init__(self, board):
        """
        :param board: GameBoard instance which is the parent.
        :type board: conquer.gameboard.GameBoard
        """
        self.board = board
        self.server = board.server

    def act(self):
        # Buy units first.
        self.buy_units_by_turn()

        # List of executed moves that is returned
        act_list = {}

        own_soldier_actor_set = set([])
        for soldier in self.board.actors:
            if not soldier.dump and soldier.side == self.board.turn \
                    and not soldier.moved:
                own_soldier_actor_set.add(soldier)
        # More CPU, more depth
        for depth in range(AI_RECURSION_DEPTH):
            # We'll iterate every actor through a copy
            for current_actor in own_soldier_actor_set.copy():
                if current_actor.dead:
                    continue
                # We'll move only own soldiers that have not moved yet
                if not current_actor.dump and not current_actor.moved \
                        and current_actor.side == self.board.turn:
                    # Memory for found move
                    m_x = None

                    # Memory for found move's points
                    m_p = 0

                    # Make a copy of the original map
                    map_copy = self.board.data.copy()
                    pisteet = []
                    koords = []
                    loppulaskija = 0
                    found_solution = False

                    possible_moves = self.board.rek.get_island_border_lands(
                        current_actor.x, current_actor.y)
                    possible_moves = list(possible_moves)
                    random.shuffle(possible_moves)

                    for coordinate_xy in possible_moves:
                        if found_solution:
                            continue
                        x2, y2 = coordinate_xy

                        # Player ID of the possible move's land
                        pala2 = self.board.data[x2, y2]

                        # Target must be enemy's land
                        if pala2 != self.board.turn and pala2 != 0:

                            # Is the move possible?
                            is_blocked = self.board.is_blocked(
                                current_actor, x2, y2)
                            if not is_blocked[0]:

                                # The move is possible, we'll simulate it
                                self.board.attempt_move(current_actor, x2, y2,
                                                        True)

                                # The points of the move
                                move_score = self.board.rek.island_size(
                                    current_actor.x, current_actor.y)

                                # Is there an actor at target land?
                                defender = self.board.actor_at(x2, y2)
                                if defender:
                                    # There is an actor at target land,
                                    # we'll add it into moves points
                                    if defender.dump and current_actor.level > 1:
                                        move_score += 5
                                        move_score += defender.supplies // 2
                                        move_score += defender.revenue - defender.expenses
                                    else:
                                        move_score += defender.level * 2

                                # Put the move and it's points in memory
                                pisteet.append(move_score)
                                koords.append((x2, y2))

                                # Restore the original map and try different moves
                                self.board.data = {}
                                self.board.data.update(map_copy)

                                # Found move better than the one in memory?
                                if move_score > m_p:
                                    # Yes it is, update
                                    m_p = move_score
                                    m_x = x2
                                if len(pisteet) > AI_RECURSION_DEPTH:
                                    # Now we have been looking move too long

                                    # If the current found move is better than
                                    # anyone else, we'll choose it
                                    if move_score > max(pisteet):
                                        m_p = move_score
                                        m_x = x2
                                        m_y = y2
                                        act_list[
                                            current_actor.x, current_actor.y] = m_x, m_y
                                        self.board.attempt_move(current_actor,
                                                                m_x, m_y, False)
                                        found_solution = True
                                        own_soldier_actor_set.discard(
                                            current_actor)
                                    # Too much used time here
                                    loppulaskija += 1
                                    if loppulaskija == AI_RECURSION_DEPTH:
                                        # We'll choose best move we have found
                                        m_p = max(pisteet)
                                        m_x = koords[pisteet.index(m_p)][0]
                                        m_y = koords[pisteet.index(m_p)][1]
                                        act_list[
                                            current_actor.x, current_actor.y] = m_x, m_y
                                        self.board.attempt_move(current_actor,
                                                                m_x, m_y, False)
                                        map_copy = self.board.data.copy()
                                        found_solution = True
                                        own_soldier_actor_set.discard(
                                            current_actor)
                    if m_x and not found_solution:
                        # Normally we shouldn't end up here, but if we
                        # do, we choose the best current move.
                        m_p = max(pisteet)
                        m_x = koords[pisteet.index(m_p)][0]
                        m_y = koords[pisteet.index(m_p)][1]
                        act_list[current_actor.x, current_actor.y] = m_x, m_y
                        self.board.attempt_move(current_actor, m_x, m_y, False)
                        own_soldier_actor_set.discard(current_actor)
        # Return dictionary of made moves
        return act_list

    def maintain_soldiers(self, city: Actor):
        """Draft and improve soldiers in the given city's island."""
        # Island's land coordinates
        place = list(self.board.rek.crawl(city.x, city.y, [city.side]))

        # Draft soldiers
        self.draft_soldiers_in_city(city, place)
        self.update_own_soldiers(city, place)

    def draft_soldiers_in_city(self, city: Actor, places):
        """Draft soldiers in the given city's island."""
        board = self.board

        # Count the amount of soldiers on the island
        soldier_count = 0
        for option in places:
            act = board.actor_at(option)
            if act and act.side == board.turn and not act.dump and not act.dead:
                soldier_count += 1

        vacant_spaces = [place for place in places if not board.actor_at(place)]

        # Heuristic: Should we buy soldiers?
        if len(vacant_spaces) > soldier_count * 3:
            # We will buy new soldiers.
            while city.supplies >= self.server.ruleset.draft_cost \
                    and city.revenue - city.expenses > 0 \
                    and vacant_spaces:
                location = random.choice(vacant_spaces)
                board.draft_soldier(location[0], location[1], sound=False)
                vacant_spaces.remove(location)

    def buy_units_by_turn(self):
        """
        This function buys and updates soldiers for CPU Players.
        """
        board = self.board

        # Iterate through a copy as original actors is probably going to be
        # modified (safe=True)
        for city in board.cities(sides=[board.turn], safe=True):
            if city.supplies >= self.server.ruleset.draft_cost:
                self.maintain_soldiers(city)

    def update_own_soldiers(self, city, places):
        board = self.board

        # When we'll stop?
        critical_cash = board.server.ruleset.draft_cost

        # Iterate through actors
        for _ in range(board.server.ruleset.max_level):
            for unit in board.actors:
                # No more income to spend?
                if city.revenue <= city.expenses or city.supplies <= critical_cash:
                    return

                if (unit.x, unit.y) in places \
                        and not unit.dump and not unit.dead \
                        and unit.side == city.side \
                        and unit.level < board.server.ruleset.max_level:
                    # Soldier is updated
                    self.board.draft_soldier(unit.x, unit.y, sound=False)
