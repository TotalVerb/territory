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

from pathlib import Path
import pygame
from .clientboard import ClientBoard
from .resources import font2, font4
from territory.configuration import ConfigurationManager
from territory.ruleset import ClassicRuleset, SlayRuleset, DefaultRuleset


class Client:
    """Primary game controller."""

    def __init__(self, screen, ih, gp, server):
        self.ih = ih
        self.screen = screen
        self.game_path = gp

        # Map
        self.board = ClientBoard(server, self, screen)

        # Configuration
        self.configuration = ConfigurationManager()
        self.board.show_cpu_moves = self.configuration.show_cpu_moves
        self.board.ai_recursion_depth = self.configuration.ai_recursion_depth

        # Connect to server
        self.server = server

        if self.configuration.ruleset == "classic":
            server.ruleset = ClassicRuleset()
        elif self.configuration.ruleset == "slay":
            server.ruleset = SlayRuleset()
        else:
            server.ruleset = DefaultRuleset()

    def load_interface_images(self):
        """Load the interface images."""
        graphics_root = Path(
            self.configuration.skin('resources.graphics', ["images"])[0])

        self.ih.add_image(
            pygame.image.load(
                str(graphics_root /
                    self.configuration.skin("screenbg.gameboard",
                                            ["gameboard.png"])[0])
            ).convert(),
            "interface"
        )
        self.ih.add_image(
            pygame.image.load(
                str(graphics_root / self.configuration.skin("screenbg.mapedit",
                                                            ["mapedit.png"])[0])
            ).convert(),
            "mapedit"
        )
        self.ih.add_image(
            pygame.image.load(
                str(graphics_root /
                    self.configuration.skin("menu.background", ["menu.png"])[0])
            ).convert(),
            "menu_interface"
        )

    def load_hextile_graphics(self):
        imagehandler = self.ih

        hextile_path = Path(
            self.configuration.skin("hextile.folder", ["images"])[0])

        # Load hextiles 1...6
        for i in range(1, 7):
            image = pygame.image.load(
                str(hextile_path / "hextile{}_.png".format(i))
            ).convert()
            image.set_colorkey(image.get_at((0, 0)))
            imagehandler.add_image(image, str(i))

    def load_unit_graphics(self):
        imagehandler = self.ih

        uisettings = self.configuration.skin("unitimage", {})
        unit_path = uisettings.get("folder", ["images"])[0] + "/"
        default_unit_path = uisettings.get("default", ["soldier.png"])[0]
        # TODO: if no need for more images, don't load them...
        for i in range(6):  # Number of possible players: 6
            uimg = \
                uisettings.get("soldier{}".format(i + 1), [default_unit_path])[
                    0]
            temppi = pygame.image.load(unit_path + uimg).convert()
            temppi.set_colorkey(temppi.get_at((0, 0)))
            imagehandler.add_image(temppi, "soldier{}".format(i + 1))

    def load_game_graphics(self):
        imagehandler = self.ih

        graphics_path = Path(
            self.configuration.skin("gfx.directory", ["images"])[0])
        temppi = pygame.image.load(
            str(graphics_path / "skull7.png")).convert_alpha()
        temppi.set_colorkey(temppi.get_at((0, 0)))
        imagehandler.add_image(temppi, "skull")
        temppi = pygame.image.load(
            str(graphics_path / "armytent.png")).convert_alpha()
        temppi.set_colorkey(temppi.get_at((0, 0)))
        imagehandler.add_image(temppi, "dump")

    def load_graphics(self):
        imagehandler = self.ih
        self.load_hextile_graphics()
        self.load_unit_graphics()
        self.load_game_graphics()

        # Load logo
        logo = self.configuration.skin("menu.logo", ["logo.png"])[0]
        logof = self.configuration.skin("menu.logofolder", ["images"])[0] + "/"
        imagehandler.add_image(pygame.image.load(logof + logo).convert_alpha(),
                               "logo")

    def text_at(self, text, coords, wipe_background=True, drop_shadow=True,
                font=font2, color=(255, 255, 255),
                flip_immediately=False, centre=False):
        """
        Render text
        text -> text to be drawn
        coords -> a tuple of coordinates (x,y)
        wipe_background=True -> draw a box behind the text
        font=font2 -> font to be used
        color = (255,255,255) -> font color
        flippaa = False -> immediately flip the screen
        """
        # Render text
        text_ = font.render(text, 1, color)

        # Metrics
        koko = font.size(text)
        text_x = coords[0] - koko[0] / 2 if centre else coords[0]

        # Wipe_Background
        if wipe_background:
            pygame.draw.rect(self.screen, (0, 0, 0),
                             (text_x, coords[1], koko[0], koko[1]))

        # Shadow
        if drop_shadow:
            shadow_text_ = font.render(text, 1, (
                255 - color[0], 255 - color[1], 255 - color[2]))
            self.screen.blit(shadow_text_, (text_x + 1, coords[1] + 1))

        # Draw the text on a screen
        self.screen.blit(text_, (text_x, coords[1]))
        if flip_immediately:
            pygame.display.flip()


    def text_input(self, caption, x1_y1, w1_h1, onlynumbers=False):
        x1, y1 = x1_y1
        w1, h1 = w1_h1
        # Make an input-box and prompt it for input
        curstr = []
        pygame.draw.rect(self.screen, (30, 30, 30), (x1, y1, w1, h1))
        self.text_at(caption, (x1 + w1 // 4, y1), font=font2,
                     wipe_background=False)
        pygame.display.flip()
        while True:
            pygame.draw.rect(self.screen, (30, 30, 30), (x1, y1, w1, h1))
            self.text_at(caption, (x1 + w1 // 4, y1), font=font2,
                         wipe_background=False)
            e = pygame.event.poll()
            if e.type == pygame.KEYDOWN:
                k = e.key
            else:
                continue

            if k == pygame.K_BACKSPACE:
                if curstr:
                    del curstr[len(curstr) - 1]
            elif k == pygame.K_RETURN:
                break
            if not onlynumbers:
                if k <= 127 and k != pygame.K_BACKSPACE:
                    curstr.append(e.unicode)
            elif k <= 127 and k != pygame.K_BACKSPACE \
                    and e.unicode in '0123456789':
                curstr.append(e.unicode)
            self.text_at("".join(curstr),
                         (((x1 + (x1 + w1)) // 2) - (len(curstr) * 4), y1 + 15),
                         wipe_background=False,
                         font=font4)
            pygame.display.flip()
        return "".join(curstr)

    def get_human_and_cpu_count(self):
        """Get how many human and cpu players will participate.

        Asks for scenario editing and random generated map.
        """

        humans = 0
        while True:
            try:
                humans = int(
                    self.text_input("How many human players (1–6)?",
                                    (800 // 2 - 110, 300), (240, 45),
                                    onlynumbers=True))
            except ValueError:
                continue
            if 1 <= humans <= 6:
                break

        cpus = 0
        low_limit = 1 if humans == 1 else 0
        hi_limit = 6 - humans
        if low_limit == hi_limit:
            return humans, low_limit

        while True:
            try:
                cpus = int(
                    self.text_input(
                        "How many CPU players (%d–%d)?" % (low_limit, hi_limit),
                        (800 // 2 - 110, 300), (240, 45), onlynumbers=True))
            except ValueError:
                continue
            if low_limit <= cpus <= hi_limit:
                break
        return humans, cpus
