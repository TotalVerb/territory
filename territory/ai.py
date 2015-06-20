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


class AI:
    def __init__(self, board):
        """
        :param board: GameBoard instance which is the parent.
        :type board: conquer.gameboard.GameBoard
        """
        self.board = board
        self.server = board.server

    def act(self, depth):
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
        for askellin in range(self.board.ai_recursion_depth):
            # We'll iterate every actor through a copy
            for current_actor in own_soldier_actor_set.copy():
                if current_actor.dead:
                    continue
                # We'll move only own soldiers that have not moved yet
                if not current_actor.dump and not current_actor.moved \
                        and current_actor.side == self.board.turn:
                    # Memory for found move
                    m_x = None
                    m_y = None

                    # Memory for found move's points
                    m_p = 0

                    # Make a copy of the original map
                    varmuuskopio = self.board.data.copy()
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
                            blokkastu = self.board.is_blocked(current_actor, x2,
                                                              y2)
                            if not blokkastu[0]:

                                # The move is possible, we'll simulate it
                                self.board.attempt_move(current_actor, x2, y2,
                                                        True)

                                # The points of the move
                                rekursiotulos = self.board.rek.recurse_own_island(
                                    current_actor.x, current_actor.y)

                                # Land area of the target island
                                vastustajan_saaren_vahvuus = self.board.rek.recurse_new_random_coord_for_dump_on_island(
                                    x2, y2)

                                # We'll favour more to conquer from large islands
                                if vastustajan_saaren_vahvuus[1]:
                                    rekursiotulos += len(
                                        vastustajan_saaren_vahvuus[1]) / 5

                                # Is there an actor at target land?
                                defender = self.board.actor_at(x2, y2)
                                if defender:
                                    # There is an actor at target land,
                                    # we'll add it into moves points
                                    if defender.dump and current_actor.level > 1:
                                        rekursiotulos += 5
                                        rekursiotulos += defender.supplies // 2
                                        rekursiotulos += defender.revenue - defender.expenses
                                    else:
                                        rekursiotulos += defender.level * 2

                                # Put the move and it's points in memory
                                pisteet.append(rekursiotulos)
                                koords.append((x2, y2))

                                # Restore the original map and try different moves
                                self.board.data = {}
                                self.board.data.update(varmuuskopio)

                                # Found move better than the one in memory?
                                if rekursiotulos > m_p:
                                    # Yes it is, update
                                    m_p = rekursiotulos
                                    m_x = x2
                                    m_y = y2
                                if len(pisteet) > depth:
                                    # Now we have been looking move too long

                                    if len(pisteet) > depth * 5:
                                        # Found no move...
                                        # This shouldn't be never executed
                                        m_x = None
                                        found_solution = True
                                        own_soldier_actor_set.discard(
                                            current_actor)
                                    # If the current found move is better than
                                    # anyone else, we'll choose it
                                    if rekursiotulos > max(pisteet):
                                        m_p = rekursiotulos
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
                                    if loppulaskija == depth:
                                        # We'll choose best move we have found
                                        m_p = max(pisteet)
                                        m_x = koords[pisteet.index(m_p)][0]
                                        m_y = koords[pisteet.index(m_p)][1]
                                        act_list[
                                            current_actor.x, current_actor.y] = m_x, m_y
                                        self.board.attempt_move(current_actor,
                                                                m_x, m_y, False)
                                        varmuuskopio = self.board.data.copy()
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

    def draft_soldiers_in_city(self, city: Actor):
        """Draft soldiers in the given city's island."""

        board = self.board

        # Has the island space for a new soldier?
        # tulos[0] new random place for actor (not checked if legal)
        # tulos[1] island's land coordinates
        tulos = board.rek.recurse_new_random_coord_for_dump_on_island(
            city.x, city.y)

        # No space for actor
        if not tulos:
            return

        # 500 tries to find a place for actor
        ok = True
        for _ in range(500):
            tulos[0] = random.choice(tulos[1])
            if not board.actor_at(tulos[0]):
                break
        else:
            ok = False

        # Count the amount of lvl<6 soldiers on the island
        levellista = []
        soldiercounter = 0
        soldiercounter2 = 0
        ykkoscount = 0
        for gctee in tulos[1]:
            hei = board.actor_at(gctee)
            if hei:
                if hei.side == board.turn and not hei.dump and not hei.dead:
                    soldiercounter2 += 1
                    if hei.level == 1:
                        ykkoscount += 1
                    if hei.level < self.server.ruleset.max_level:
                        soldiercounter += 1
                        levellista.append(hei.level)

        # Does the island has upgradable soldiers (lvl<6)?
        if soldiercounter != 0:
            # When the island has soldiers, it is more likely
            # to update them. 66% chance to update existing
            # soldiers.
            if random.randint(1, 3) != 2:
                ok = False

        vapaat_maat = []
        for gctee in tulos[1]:
            if not board.actor_at(gctee):
                vapaat_maat.append(gctee)

        # Do we have any soldiers at all?
        if soldiercounter2 != 0:
            # We do, count how many free lands there are per soldier
            suhde = len(vapaat_maat) // soldiercounter2
            # If three or more, we need new soldiers
            if suhde >= 3:
                ok = False
                tries = 0
                while not ok and tries < 500:
                    tries += 1
                    tulos[0] = random.choice(tulos[1])
                    if not board.actor_at(tulos[0]):
                        ok = True
            # We have probably enough soldiers so update them
            if suhde <= 2:
                ok = False

        # BUT If we have upgradable soldiers AND over half of the
        # possible attack targets need better soldiers, we'll
        # update soldiers :)
        # FIXME: pretty complicated
        paatos = False
        tooweakcount = 0
        a_searched = []
        if soldiercounter > 0:
            unit = Actor(0, 0, board.turn, level=0, dump=False)
            for xy in tulos[1]:
                for nx, ny in board.neighbours(xy[0], xy[1]):
                    if board.validxy(nx, ny):
                        if (nx, ny) in a_searched:
                            continue
                        if board.data[nx, ny] != board.turn:
                            a_searched.append((nx, ny))
                            unit.x, unit.y, side = xy[0], xy[1], board.turn
                            found_hardguy = soldiercounter
                            for haastaja in levellista:
                                unit.level = haastaja
                                if board.is_blocked(
                                        unit, nx, ny)[3] == "tooweak":
                                    found_hardguy -= 1
                            if found_hardguy == 0:
                                tooweakcount += 1
            if float(tooweakcount) / float(len(a_searched)) >= 0.3:
                ok = False
                paatos = True

        # But if we don't have any soldiers, we'll buy them...
        if soldiercounter2 == 0:
            ok = True

        # We still shouldn't buy too much
        if city.revenue - city.expenses < 1:
            return

        if ok:
            # Okay, WE WILL BUY NEW SOLDIERS
            m11 = random.randint(1, 2) * self.server.ruleset.draft_cost
            m22 = random.randint(0, 1)
            # Little variation...
            tries = 0
            while city.supplies >= m11 \
                    and city.revenue - city.expenses > m22:
                ok2 = False
                while not ok2 and tries < 500:
                    tries += 1
                    tulos[0] = random.choice(tulos[1])
                    if not board.actor_at(tulos[0]):
                        ok2 = True
                if ok2:
                    # Add new soldier and make financial calculus

                    unit = board.draft_soldier(tulos[0][0], tulos[0][1],
                                               sound=False)

                    # 90% - (lvl*10%) chance to update it
                    # So mathematically possibility to update straight to level6:
                    # 0.8 * 0.7 * 0.6 * 0.5 * 0.4 = 7%
                    # Straight to level5:
                    # 17%
                    # Straight to level4:
                    # 34%
                    # And so on...

                    while city.supplies >= self.server.ruleset.draft_cost \
                            and city.revenue > city.expenses \
                            and unit.level < self.server.ruleset.max_level:
                        if random.randint(1, 10) <= 9 - unit.level:
                            self.board.draft_soldier(
                                tulos[0][0], tulos[0][1], sound=False)
                        else:
                            break

            # If we didn't buy with every supplies, we can update soldiers
            if m11 or m22:
                self.update_own_soldiers(city, tulos, ykkoscount,
                                         soldiercounter2, paatos)
        else:
            self.update_own_soldiers(city, tulos, ykkoscount,
                                     soldiercounter2, paatos)

    def buy_units_by_turn(self):
        """
        This function buys and updates soldiers for CPU Players.
        """

        board = self.board

        # This is VERY MESSY function, cleaning will be done sometime

        # Iterate through a copy as original actors is probably going to be
        # modified (safe=True)
        for city in board.cities(sides=[board.turn], safe=True):
            if city.supplies >= self.server.ruleset.draft_cost:
                self.draft_soldiers_in_city(city)

    def update_own_soldiers(self, city, tulos, ykkoscount, soldiercounter2,
                            paatos):
        board = self.board

        # Update soldiers with supplies
        tries = 0

        # When we'll stop?
        critical_cash = board.server.ruleset.draft_cost

        running = True
        # We'll update as long as supplies are used or panic has arisen
        while city.supplies > critical_cash and running:
            tries += 1
            # We'll try one hundred times
            if tries == 100:
                running = False

            # Iterate through actors
            for unit in board.actors:
                # Panic - button has been pressed ;)
                if not running:
                    break

                # No more income to spend?
                if city.revenue <= city.expenses:
                    running = False
                    break

                if (unit.x, unit.y) in tulos[1] \
                        and not unit.dump and not unit.dead \
                        and unit.side == city.side:
                    # Level 6 are not updated, level 1 have better chance to be updated.
                    # But if we just need better soldiers we'll update everyone (paatos).
                    if unit.level < board.server.ruleset.max_level:
                        # Level 1 soldiers found
                        if ykkoscount > 0 and (
                                    soldiercounter2 - ykkoscount) > 0:
                            if unit.level == 1:
                                # No critical need for updates?
                                if not paatos:
                                    # 25% change to not to update lvl1
                                    if random.randint(1, 4) != 2:
                                        # EI-Ykkosille enemman prioriteettia
                                        continue

                        # Soldier is updated
                        self.board.draft_soldier(unit.x, unit.y, sound=False)

                        # Panic with supplies?
                        if city.supplies <= critical_cash \
                                or city.revenue - city.expenses <= 0:
                            running = False
