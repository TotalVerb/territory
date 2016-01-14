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
from .resources import font4, font2, mono_font, font3, font1
from .cursor import Cursor
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
        super().__init__(server)

        self.client = client

        # Pygame screen surface passed as "pointer" for drawing methods
        self.screen = screen

        # Instance of cursor
        self.cursor = Cursor(self, self.client)
        self.cursor.x = 10
        self.cursor.y = 10

        # Options
        self.show_cpu_moves = False

    @property
    def sc(self):
        """The skin configuration."""
        # delegate to configuration manager
        warnings.warn("Access to deprecated property sc.",
                      category=DeprecationWarning)
        return self.client.configuration.sc

    def new_game(self, scenariofile="unfair", randommap=False,
                 randomplayers_cpu=3, humanplayers=3):
        super().new_game(scenariofile, randommap, randomplayers_cpu,
                         humanplayers)

        self.cursor.scroll_x = 0

        self.drawmap()
        # Calculate and sort scores and draw scores
        self.draw_scoreboard(True)

        pygame.display.flip()

        # If the first player is computer, make it act
        if self.playerlist[0].ai_controller:
            # The AI routines for CPU Player are called from it's AI-Controller
            self.playerlist[0].ai_controller.act(self.ai_recursion_depth)
            # FIXME, cpu intensive?
            # Well anyway, make sure that dumps are on their places
            self.fill_dumps()
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
                    act_dict = player.ai_controller.act(self.ai_recursion_depth)

                    self.drawmap()

                    # Draw CPU player's moves
                    if self.show_cpu_moves_with_lines:
                        for key, value in act_dict.items():
                            if self.seenxy(key[0], key[1]) and self.seenxy(
                                    value[0],
                                    value[1]):
                                px1, py1 = hexMapToPixel(
                                    key[0] - self.cursor.scroll_x, key[1])
                                px2, py2 = hexMapToPixel(
                                    value[0] - self.cursor.scroll_x, value[1])
                                pygame.draw.line(self.screen, (255, 0, 0),
                                                 (px1 + 20, py1 + 20),
                                                 (px2 + 20, py2 + 20), 2)

                    self.draw_scoreboard(True)
                    pygame.display.flip()
                    time.sleep(0.35)  # give some time to view
                    self.end_turn()
                else:
                    self.drawmap()
                    self.draw_scoreboard(True)
                    pygame.display.flip()
                if player.won:
                    self.draw_scoreboard(False)
                    pygame.display.flip()

            # Iterate through events
            for eventti in pygame.event.get():
                # Mouse click
                if eventti.type == pygame.MOUSEBUTTONDOWN:
                    x1, y1 = pixelToHexMap(eventti.pos)
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
                self.drawmap()
                # Show the drawed content
                pygame.display.flip()

    def seenxy(self, x, y):
        """Return True if the coordinate is currently seen by player."""
        # (not scrolled out of borders)
        return (0 + self.cursor.scroll_x) <= x <= (14 + self.cursor.scroll_x)

    def draw_map_edit_utilities(self):
        # Extra drawing routines for scenario editing mode

        # Text for selected map tile
        if self.map_edit_info[2] == 0:
            tool_name = "Eraser"
        else:
            if self.map_edit_info[2] <= (
                        self.map_edit_info[0] + self.map_edit_info[1]):
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

    def drawmap(self):
        """
        Game window's drawing routines
        """

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
                    px, py = hexMapToPixel(x - self.cursor.scroll_x, y)

                    # Draw the piece
                    self.screen.blit(self.client.ih.gi(str(self.data[x, y])),
                                     (px, py))

                    # Check if actor is found at the coordinates
                    actor = self.actor_at(x, y)
                    if actor:
                        if actor.dump:
                            # a Resource Dump was found
                            self.screen.blit(self.client.ih.gi("dump"),
                                             (px + 3, py + 8))

                            # If the dump is on our side and we are not AI controlled, then we'll
                            # draw the supply count on the dump.
                            if actor.side == self.turn and not self.get_player_by_side(
                                    actor.side).ai_controller:
                                # self.text_at("%d"%actor.supplies,(px+16,py+11),font=font2,color=(0,0,0),wipe_background = False)
                                self.text_at(str(actor.supplies),
                                             (px + 15, py + 13),
                                             font=font2,
                                             wipe_background=False)
                        else:
                            # a Soldier was found
                            # Make a text for soldier-> level and X if moved
                            teksti = str(actor.level)
                            if actor.moved:
                                teksti += "X"
                            # Draw soldier
                            self.screen.blit(
                                self.client.ih.gi("soldier" + str(actor.level)),
                                (px, py))
                            # Draw text for the soldier
                            self.text_at(teksti, (px + 20, py + 20),
                                         font=font1)
        # If an actor is selected, then we'll draw red box around the actor
        if self.cursor.chosen_actor:
            px, py = hexMapToPixel(self.cursor.x - self.cursor.scroll_x,
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

    def text_at(self, text, coords, wipe_background=True, drop_shadow=True,
                font=font2, color=(255, 255, 255),
                flip_immediately=False):
        self.client.text_at(text, coords, wipe_background, drop_shadow,
                            font, color, flip_immediately)

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
            self.pisteet_s = sorted(scores.items(), key=itemgetter(1))

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
        for jau in reversed(self.pisteet_s):
            # I split the lines here, see the last comma
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
        try:
            # Lost players are discarded from playerlist, so next line may
            # raise an error.
            tahko = self.get_player_by_side(self.turn)
            # Human player
            if not tahko.ai_controller:
                if not tahko.lost:
                    # Human player's turn, tell it
                    self.text_at("Your (%s) turn" % tahko.name, (630, 300),
                                 color=(0, 0, 0),
                                 font=font3, wipe_background=False)
                else:
                    # The human player has lost, tell it
                    self.text_at("You (%s) lost..." % tahko.name, (635, 300),
                                 color=(0, 0, 0),
                                 font=font3, wipe_background=False)
        except:
            # Error occurred, well do nothing about it...
            pass

    def show_own_units_that_can_move(self):
        # Draw own units that have not moved yet
        for actor in self.actors:
            if not actor.moved and actor.side == self.turn and not actor.dump:
                if self.seenxy(actor.x, actor.y):
                    pixelX, pixelY = hexMapToPixel(
                        actor.x - self.cursor.scroll_x, actor.y)
                    pygame.draw.circle(self.screen, (255, 255, 20),
                                       (pixelX + 20, pixelY + 20), 20, 3)
        pygame.display.flip()
        time.sleep(0.5)
        self.drawmap()

    def attempt_move(self, actor, x2, y2, only_simulation):
        result = super().attempt_move(actor, x2, y2, only_simulation)

        # Warn if attacker is seen on the screen
        if isinstance(result, BlockedResponse):
            x, y = result.reason_x, result.reason_y

            if self.seenxy(x, y):
                # Clear selected actor
                self.cursor.chosen_actor = None
                # Convert (scrolled) hex map coordinates into screen pixels
                # and draw circle there
                pixelX, pixelY = hexMapToPixel(x - self.cursor.scroll_x, y)
                pygame.draw.circle(self.screen, (0, 255, 0),
                                   (pixelX + 20, pixelY + 20), 30, 2)
                self.text_at(block_desc(result.reason), (pixelX, pixelY + 15),
                             font=font2)
                pygame.display.flip()
                # Little time to actually see it
                time.sleep(0.35)
                self.drawmap()
                pygame.display.flip()


def pixelToHexMap(x_y):
    x, y = x_y
    gridX = x // hex_system.GRID_WIDTH
    gridY = y // hex_system.GRID_HEIGHT
    gridPixelX = x % hex_system.GRID_WIDTH
    gridPixelY = y % hex_system.GRID_HEIGHT
    if gridY & 1:
        hexMapX = gridX + hex_system.gridOddRows[gridPixelY][gridPixelX][0]
        hexMapY = gridY + hex_system.gridOddRows[gridPixelY][gridPixelX][1]
    else:
        hexMapX = gridX + hex_system.gridEvenRows[gridPixelY][gridPixelX][0]
        hexMapY = gridY + hex_system.gridEvenRows[gridPixelY][gridPixelX][1]
    return hexMapX, hexMapY


def hexMapToPixel(mapX, mapY):
    """
    Returns the top left pixel location of a hexagon map location.
    """
    if mapY & 1:
        # Odd rows will be moved to the right.
        return mapX * hex_system.TILE_WIDTH + hex_system.ODD_ROW_X_MOD, mapY * hex_system.ROW_HEIGHT
    else:
        return mapX * hex_system.TILE_WIDTH, mapY * hex_system.ROW_HEIGHT
