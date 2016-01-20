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


class Cursor:
    """The mouse cursor in-game."""

    def __init__(self, board: "territory.client.clientboard.ClientBoard",
                 client):
        self.x = 10
        self.y = 10
        self.scroll_x = 0
        self.chosen_actor = None
        self.chosen_dump = None
        self.board = board
        self.client = client
        self.mouse_pos = (0, 0)

    def scroll(self, dx):
        self.scroll_x += dx
        if self.scroll_x > 15:
            self.scroll_x = 15
        if self.scroll_x < 0:
            self.scroll_x = 0

    def click(self):
        mx = self.mouse_pos[0]
        my = self.mouse_pos[1]

        if not self.board.map_edit_mode:
            # We are not in map editing mode, so we check from
            # skin configuration file if we clicked any gui elements.
            bet = self.board.sc["button_endturn"]
            if bet[0][0] <= mx <= bet[1][0] \
                    and bet[0][1] <= my <= bet[1][1]:
                self.board.end_turn()
            bq = self.board.sc["button_quit"]
            if bq[0][1] <= my <= bq[1][1] \
                    and bq[0][0] <= mx <= bq[1][0]:
                self.chosen_actor = None
                self.chosen_dump = None
                self.board.end_game()
            if mx < 573 and my < 444:
                if self.chosen_actor:
                    self.board.attempt_move(self.chosen_actor, self.x, self.y,
                                            False)
                    self.board.destroy_lonely_actors()
                    self.board.has_anyone_lost_the_game()
                    if self.board.check_and_mark_if_someone_won():
                        self.board.data = {}
                        self.board.actors.clear()
                        self.board.fill_map(0)
                        return
                else:
                    # Do we have clicked our own soldier?
                    actor = self.board.actor_at(self.x, self.y)
                    if actor:
                        if not actor.dump:
                            if actor.side == self.board.turn:
                                # Yes we have, choose it
                                self.chosen_actor = actor
                                return
                        else:
                            if actor.side == self.board.turn:
                                self.chosen_dump = actor
                                return
            self.chosen_actor = None
            self.chosen_dump = None
        else:
            # Have we clicked gui elements?
            # FIXME: change editor gui elements to be modded with skin-file
            if 620 <= mx <= 782 and 366 <= my <= 416:
                # "Save Map" pressed
                map_name = self.client.text_input(
                    "[SAVE MAP] Map name?", (800 / 2 - 110, 300), (240, 45))
                self.board.write_edit_map(
                    self.client.game_path / "scenarios" / map_name)
            if 618 <= mx <= 782 and 429 <= my <= 472:
                # "Load Map" pressed
                map_name = self.client.text_input(
                    "[LOAD MAP] Map name?", (800 / 2 - 110, 300), (240, 45))
                load_path = self.client.game_path / "scenarios" / map_name
                if load_path.is_file():
                    self.board.load_map(load_path)
            if 607 <= mx <= 792 and 560 <= my <= 591:
                # "Quit" pressed
                self.board.running = False
            if mx < 573 and my < 444:
                # Map editor pressed
                if 0 < self.x < 29 and 0 < self.y < 13:
                    self.board.data[self.x, self.y] = self.board.map_edit_info[
                        2]

    def get_color(self):
        if self.chosen_actor:
            return 255, 0, 0
        else:
            return 255, 255, 255


import territory.client.clientboard
