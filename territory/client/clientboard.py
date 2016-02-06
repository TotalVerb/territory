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
from operator import itemgetter
import warnings
import time

import pygame

from territory import soundtrack, hex_system
from .cursor import Cursor
from .resources import font4, font2, mono_font, font3, font1
from territory.gameboard import GameBoard
from territory.ruleset import BlockedResponse
from territory.server import Server

BLOCK_DESCRIPTIONS = {
    "tooweak": "Your soldier is too weak!",
    "sameside": "Target is friendly!",
    "alreadymoved": "Soldier has already moved!",
    "spaceisnotlegal": "Target is not land!",
    "outofisland": "Out of soldiers reach!",
    "nullmove": "Cannot move to own square!"
}


def block_desc(r):
    """Get reason for being blocked."""
    return BLOCK_DESCRIPTIONS.get(r, "Blocked.")


class ClientBoard(GameBoard):
    """A game board with drawing capacities."""

    def __init__(self, server: Server, client, screen):
        super().__init__(server, server.ruleset)

        self.client = client

        # Pygame screen surface for drawing methods
        self.screen = screen

        # Instance of cursor
        self.cursor = Cursor(self, self.client)
        self.cursor.x = 10
        self.cursor.y = 10

        # Options
        self.show_cpu_moves = False

        # If the game (actual map view) is running, running is True
        self.running = False

    @property
    def sc(self):
        """The skin configuration."""
        # delegate to configuration manager
        warnings.warn("Access to deprecated property sc.",
                      category=DeprecationWarning)
        return self.client.configuration.sc

    def end_game(self):
        # Set gamerunning to false and reset to regular music
        self.running = False
        soundtrack.play_soundtrack("soundtrack")

    def new_game(self, *args, **kwargs):
        super().new_game(*args, **kwargs)

        self.cursor.scroll_x = 0

        self.draw_map()
        # Calculate and sort scores and draw scores
        self.draw_scoreboard(True)

        pygame.display.flip()

        # If the first player is computer, make it act
        if self.playerlist[0].ai_controller:
            # The AI routines for CPU Player are called from it's AI-Controller
            self.playerlist[0].ai_controller.act()
            # Well anyway, make sure that dumps are on their places
            self.land_was_conquered()
            # Next player's turn
            self.end_turn()

    def start_game(self):
        self.running = True
        # Begin the march music
        soundtrack.play_soundtrack("march")

        # Instance of pygame's Clock
        clock = pygame.time.Clock()

        # The Main Loop to run a game
        while self.running:

            # Limit fps to 30, smaller resource usage
            clock.tick(30)

            player = self.get_player_by_side(self.turn)
            if player:
                if player.lost:
                    self.end_turn()
                elif player.ai_controller:
                    kolorissi = tuple(self.sc["making_moves_text_color"])
                    self.text_at("Player %s is making moves..." % player.name,
                                 tuple(self.sc[
                                           "making_moves_text_topleft_corner"]),
                                 flip_immediately=True, font=font3,
                                 wipe_background=False,
                                 color=kolorissi)

                    # Here the AI makes moves
                    act_dict = player.ai_controller.act()

                    self.draw_map()

                    # Draw CPU player's moves
                    if self.show_cpu_moves_with_lines:
                        for key, value in act_dict.items():
                            if self.isvisible(key[0],
                                              key[1]) and self.isvisible(
                                    value[0],
                                    value[1]):
                                px1, py1 = hex_map_to_pixel(
                                    key[0] - self.cursor.scroll_x, key[1])
                                px2, py2 = hex_map_to_pixel(
                                    value[0] - self.cursor.scroll_x, value[1])
                                pygame.draw.line(self.screen, (255, 0, 0),
                                                 (px1 + 20, py1 + 20),
                                                 (px2 + 20, py2 + 20), 2)

                    self.draw_scoreboard(True)
                    pygame.display.flip()
                    time.sleep(0.35)  # give some time to view
                    self.end_turn()
                else:
                    self.draw_map()
                    self.draw_scoreboard(True)
                    pygame.display.flip()
                if player.won:
                    self.draw_scoreboard(False)
                    pygame.display.flip()

            # Iterate through events
            for eventti in pygame.event.get():
                # Mouse click
                if eventti.type == pygame.MOUSEBUTTONDOWN:
                    x1, y1 = pixel_to_hex_map(eventti.pos)
                    # Scrolling included in calculations
                    x1 += self.cursor.scroll_x
                    # Coordinates into cursor's memory
                    self.cursor.x, self.cursor.y = x1, y1
                    self.cursor.mouse_pos = eventti.pos

                    # Left mouse button = cursor's click
                    if eventti.button == 1:
                        self.cursor.click()
                    # Right mouse button = draft and update soldiers if
                    # NOT in map editing mode
                    if not self.map_edit_mode:
                        if eventti.button == 3 and y1 < 15 and x1 < 30:
                            self.draft_soldier(self.cursor.x, self.cursor.y)
                # Key press
                if eventti.type == pygame.KEYDOWN:
                    if eventti.key == pygame.K_LEFT:
                        # Scroll screen left
                        self.cursor.scroll(-1)
                    if eventti.key == pygame.K_RIGHT:
                        # Scroll screen right
                        self.cursor.scroll(1)

                    if not self.map_edit_mode:
                        if eventti.key == pygame.K_m:
                            self.show_own_units_that_can_move()
                        if eventti.key == pygame.K_e:
                            self.end_turn()
                    else:
                        # In map editor mode, UP and DOWN keys change
                        # selected land
                        if eventti.key == pygame.K_UP:
                            self.map_edit_info[2] += 1
                            if self.map_edit_info[2] > 6:
                                self.map_edit_info[2] = 6
                        if eventti.key == pygame.K_DOWN:
                            self.map_edit_info[2] -= 1
                            if self.map_edit_info[2] < 0:
                                self.map_edit_info[2] = 0
                # Draw the scoreboard without calculating and sorting scores
                self.draw_scoreboard(False)
                # Draw the map
                self.draw_map()
                # Show the drawn content
                pygame.display.flip()

    def isvisible(self, x, y):
        """Return True if the coordinate is currently visible by player."""
        return 0 + self.cursor.scroll_x <= x <= 14 + self.cursor.scroll_x

    def draw_map_edit_utilities(self):
        # Extra drawing routines for scenario editing mode

        # Text for selected map tile
        if self.map_edit_info[2] == 0:
            tool_name = "Eraser"
        else:
            if self.map_edit_info[2] <= \
                            self.map_edit_info[0] + self.map_edit_info[1]:
                tool_name = "Player #%d land" % self.map_edit_info[2]
            else:
                # Land without player in the map, good for connecting player
                # islands in own maps.
                tool_name = "Land #%d without player" % self.map_edit_info[2]

        # Show the selected map tile text
        self.text_at("Selected:", (620, 80), font=font4,
                     wipe_background=False, color=(0, 0, 0))
        self.text_at(tool_name, (620, 100), font=font4, wipe_background=False,
                     color=(0, 0, 0))

        # Draw players captions in the scenario
        counter = 0
        for i in range(0, self.map_edit_info[0]):
            counter += 1
            self.text_at("Player #%d = Human" % counter,
                         (620, 130 + counter * 20), font=font4,
                         wipe_background=False,
                         color=(0, 0, 0))
        for i in range(0, self.map_edit_info[1]):
            counter += 1
            self.text_at("Player #%d = CPU" % counter,
                         (620, 130 + counter * 20), font=font4,
                         wipe_background=False,
                         color=(0, 0, 0))
        if (6 - counter) > 0:
            for i in range(0, (6 - counter)):
                counter += 1
                self.text_at("Player #%d = No player" % counter,
                             (620, 130 + counter * 20), font=font4,
                             wipe_background=False, color=(0, 0, 0))

    def draw_actor(self, actor, px, py):
        if actor.dump:
            # a Resource Dump was found
            self.screen.blit(self.client.ih.gi("dump"), (px + 3, py + 8))

            # If the dump is on our side and we are not AI controlled, then
            # we'll draw the supply count on the dump.
            if actor.side == self.turn and not self.get_player_by_side(
                    actor.side).ai_controller:
                self.text_at(str(actor.supplies),
                             (px + 15, py + 13),
                             font=font2,
                             wipe_background=False)
        else:
            # a Soldier was found
            # Make a text for soldier-> level and X if moved
            text = str(actor.level)
            if actor.moved:
                text += "X"
            # Draw soldier
            self.screen.blit(
                self.client.ih.gi("soldier" + str(actor.level)),
                (px, py))
            # Draw text for the soldier
            self.text_at(text, (px + 20, py + 20), font=font1)

    def draw_map(self):
        """Draw the interface."""

        # Draw the correct interface
        if not self.map_edit_mode:
            # Game interface
            self.screen.blit(self.client.ih.gi("interface"), (0, 0))
            self.draw_scoreboard(False)
        else:
            # Map editing interface
            self.screen.blit(self.client.ih.gi("mapedit"), (0, 0))
            self.draw_map_edit_utilities()

        # Loop pieces to be drawn (horizontally there is scrolling too)
        for x in range(self.cursor.scroll_x, 15 + self.cursor.scroll_x):
            for y in range(14):
                # There is land to draw
                if self.data[x, y] > 0:

                    # Get pixel coordinates
                    px, py = hex_map_to_pixel(x - self.cursor.scroll_x, y)

                    # Draw the piece
                    self.screen.blit(self.client.ih.gi(str(self.data[x, y])),
                                     (px, py))

                    # Check if actor is found at the coordinates
                    actor = self.actor_at(x, y)
                    if actor:
                        self.draw_actor(actor, px, py)
        # If an actor is selected, then we'll draw red box around the actor
        if self.cursor.chosen_actor:
            px, py = hex_map_to_pixel(self.cursor.x - self.cursor.scroll_x,
                                      self.cursor.y)
            pygame.draw.rect(self.screen, self.cursor.get_color(),
                             (px, py, 40, 40), 2)

        # If an dump is chosen, we'll draw information about it:
        #   Revenues, Expenses, Supplies
        if self.cursor.chosen_dump:
            text_colour = tuple(self.sc["unit_status_text_color"])
            x1, y1 = self.sc["unit_status_text_topleft_corner"]
            self.text_at("Resource dump", (x1, y1 + 30), font=font4,
                         wipe_background=False, color=text_colour)
            self.text_at("Revenues: %d" % self.cursor.chosen_dump.revenue,
                         (x1, y1 + 50), font=font4,
                         wipe_background=False, color=text_colour)
            self.text_at("Expenses: %d" % self.cursor.chosen_dump.expenses,
                         (x1, y1 + 70), font=font4,
                         wipe_background=False, color=text_colour)
            self.text_at("Supplies: %d" % self.cursor.chosen_dump.supplies,
                         (x1, y1 + 90), font=font4,
                         wipe_background=False, color=text_colour)
            self.screen.blit(self.client.ih.gi("dump"), (x1, y1))

    def text_at(self, *args, **kwargs):
        self.client.text_at(*args, **kwargs)

    def draw_scoreboard(self, update=False):
        """
        Draw Scoreboard
        update -> If true, scores are calculated and sorted
        """
        if update:
            # Update scores
            scores = {}
            for peluri in self.playerlist:
                if not peluri.lost:
                    # Count existing players land count
                    scores[peluri] = self.whole_map_situation_score(peluri.id)
            # Sort points
            self.scores = sorted(scores.items(), key=itemgetter(1))

        # Iterate every player
        for player in self.playerlist:
            # Check if a player has won
            if player.won:
                # a Player has won, show the information
                self.cursor.chosen_actor = None
                self.cursor.chosen_dump = None
                if player.ai_controller:
                    self.text_at("%s won the game!" % player.name,
                                 (200, 200), font=font4,
                                 color=(255, 255, 255))
                else:
                    self.text_at("You (%s) won the game!" % player.name,
                                 (200, 200), font=font4,
                                 color=(255, 255, 255))
                pygame.display.flip()

        counter = 0
        # Draw the scores, counter puts text in right row.
        # Skin configuration file is used here
        for jau in reversed(self.scores):
            self.screen.blit(
                self.client.ih.gi("%d" % jau[0].id), (
                    self.sc["scoreboard_text_topleft_corner"][0],
                    self.sc["scoreboard_text_topleft_corner"][
                        1] + 35 * counter - 13))

            self.text_at("{:<4}{}".format(jau[1], jau[0].name),
                         (self.sc["scoreboard_text_topleft_corner"][0] + 15,
                          self.sc["scoreboard_text_topleft_corner"][
                              1] + 35 * counter),
                         color=(self.sc["scoreboard_text_color"][0],
                                self.sc["scoreboard_text_color"][1],
                                self.sc["scoreboard_text_color"][2]),
                         font=mono_font,
                         wipe_background=False)

            counter += 1

        player = self.get_player_by_side(self.turn)

        # Check for human; note lost players are discarded from player list
        if player and not player.ai_controller:
            if not player.lost:
                # Human player's turn, tell it
                self.text_at("Your (%s) turn" % player.name, (630, 300),
                             color=(0, 0, 0),
                             font=font3, wipe_background=False)
            else:
                # The human player has lost, tell it
                self.text_at("You (%s) lost..." % player.name, (635, 300),
                             color=(0, 0, 0),
                             font=font3, wipe_background=False)

    def show_own_units_that_can_move(self):
        # Draw own units that have not moved yet
        for actor in self.actors:
            if not actor.moved and actor.side == self.turn and not actor.dump:
                if self.isvisible(actor.x, actor.y):
                    px, py = hex_map_to_pixel(
                        actor.x - self.cursor.scroll_x, actor.y)
                    pygame.draw.circle(self.screen, (255, 255, 20),
                                       (px + 20, py + 20), 20, 3)
        pygame.display.flip()
        time.sleep(0.5)
        self.draw_map()

    def attempt_move(self, actor, x2, y2, only_simulation):
        result = super().attempt_move(actor, x2, y2, only_simulation)

        # Warn if attacker is seen on the screen
        if isinstance(result, BlockedResponse):
            x, y = result.reason_x, result.reason_y

            if self.isvisible(x, y):
                # Clear selected actor
                self.cursor.chosen_actor = None
                # Convert (scrolled) hex map coordinates into screen pixels
                # and draw circle there
                px, py = hex_map_to_pixel(x - self.cursor.scroll_x, y)
                pygame.draw.circle(self.screen, (0, 255, 0),
                                   (px + 20, py + 20), 30, 2)
                self.text_at(block_desc(result.reason), (px, py + 15),
                             font=font2)
                pygame.display.flip()
                # Little time to actually see it
                time.sleep(0.35)
                self.draw_map()
                pygame.display.flip()


def pixel_to_hex_map(x_y):
    x, y = x_y
    grid_x = x // hex_system.GRID_WIDTH
    grid_y = y // hex_system.GRID_HEIGHT
    grid_pixel_x = x % hex_system.GRID_WIDTH
    grid_pixel_y = y % hex_system.GRID_HEIGHT
    if grid_y & 1:
        hx = grid_x + hex_system.GRID_ODD_ROWS[grid_pixel_y][grid_pixel_x][0]
        hy = grid_y + hex_system.GRID_ODD_ROWS[grid_pixel_y][grid_pixel_x][1]
    else:
        hx = grid_x + hex_system.GRID_EVEN_ROWS[grid_pixel_y][grid_pixel_x][0]
        hy = grid_y + hex_system.GRID_EVEN_ROWS[grid_pixel_y][grid_pixel_x][1]
    return hx, hy


def hex_map_to_pixel(x, y):
    """
    Returns the top left pixel location of a hexagon map location.
    """
    if y & 1:
        # Odd rows will be moved to the right.
        return x * hex_system.TILE_WIDTH + hex_system.ODD_ROW_X_MOD, y * hex_system.ROW_HEIGHT
    else:
        return x * hex_system.TILE_WIDTH, y * hex_system.ROW_HEIGHT
