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
import collections
import random
from territory.actor import Actor

BlockedResponse = collections.namedtuple(
    'BlockedResponse',
    ['blocked', 'reason_x', 'reason_y', 'reason']
)


class DefaultRuleset:
    """Modern ruleset."""
    allow_merge = True
    max_level = 6
    upkeep_costs = {
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 7
    }
    draft_cost = 2

    def is_blocked(self, board, actor, x, y):
        """Check if coordinate(x, y) is blocked for the actor."""

        defender = board.actor_at(x, y)

        if defender:
            if defender is actor:
                # We need this case because otherwise low units could "merge"
                # with themselves!
                return BlockedResponse(True, x, y, "nullmove")
            elif defender.side == actor.side:
                assert board.data[x, y] == board.turn
                # One can't conquer his own soldiers, but merge may be possible
                if self.allow_merge and not defender.dump \
                        and defender.level + actor.level <= self.max_level:
                    return BlockedResponse(False, 0, 0, "legal")
                else:
                    return BlockedResponse(True, x, y, "sameside")
            else:
                assert board.data[x, y] != board.turn
                # There is an enemy defending unit at target
                if actor.level < self.max_level:
                    if defender.level >= actor.level:
                        return BlockedResponse(True, x, y, "tooweak")

                if defender.dump and actor.level < 2:
                    return BlockedResponse(True, x, y, "tooweak")

        # Soldier can move only once a turn
        if actor.moved:
            return BlockedResponse(True, x, y, "alreadymoved")

        # Empty Space can't be conquered
        if board.data[x, y] == 0:
            return BlockedResponse(True, x, y, "spaceisnotlegal")

        # Set that holds recursed land piece coordinates
        crawl_list = set()

        # Recurse every land on the island where attacking soldier is
        board.rek.crawl(actor.x, actor.y, crawl_list, [board.turn])

        found = False
        edm = board.get_right_edm(y)
        for i in range(6):
            if board.isvalid(x + edm[i][0], y + edm[i][1]):
                # Next to target must be own land. The land must be
                # from the same island as the actor is from.
                if (x + edm[i][0], y + edm[i][1]) in crawl_list:
                    found = True
        if not found:
            # No adjacent lands found, can't conquer places out of
            # soldier's reach
            return BlockedResponse(True, x, y, "outofisland")

        # Check for enemy unit blockers
        for i in range(6):
            # Is the coordinate valid?
            if board.isvalid(x + edm[i][0], y + edm[i][1]):
                # Is the targets neighbour same side as the target
                if board.data[x + edm[i][0], y + edm[i][1]] == board.data[x, y]:
                    # Has the neighbour's adjacent own piece a soldier
                    # defending?
                    defenderi = board.actor_at(x + edm[i][0], y + edm[i][1])
                    if defenderi and defenderi.side != actor.side:
                        # Yes it has
                        if defenderi.dump and actor.level == 1:
                            # Dump can defend against level 1 soldiers
                            # Attacker is level 1, blocked = True
                            return BlockedResponse(
                                True, x + edm[i][0], y + edm[i][1], "tooweak")
                        if actor.level < self.max_level \
                                and defenderi.level >= actor.level:
                            # Attacker's level is under MAX
                            # (level MAX can attack where-ever it wants)
                            # Attacker's soldier is weaker than defender,
                            # blocked=True
                            return BlockedResponse(
                                True, x + edm[i][0], y + edm[i][1], "tooweak")
        # Found nothing that could block attacker,
        # blocked = False !!! The move is legal.
        return BlockedResponse(False, 0, 0, "legal")

    def takeover_attempt(self, actor: Actor, target: Actor):
        """Return True if actor successfully takes over target.

        This function may be probabilistic and only return True some of the
        time.
        """
        if target.dump:
            return actor.level >= 2
        elif actor.level == self.max_level and target.level == self.max_level:
            # 50% chance to win or lose
            return random.random() < 0.5
        else:
            return actor.level > target.level


class ClassicRuleset(DefaultRuleset):
    """Ruleset that mimics Conquer as best as possible."""
    allow_merge = False
    draft_cost = 1


class SlayRuleset(DefaultRuleset):
    """Ruleset that mimics Slay as best as possible."""
    max_level = 4
    upkeep_costs = {
        1: 2,
        2: 6,
        3: 18,
        4: 54
    }
    draft_cost = 10
