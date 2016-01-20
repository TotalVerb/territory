#!/usr/bin/python3
# Territory is a strategy-flavoured game written with PyGame

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
import time
from sys import path
from pathlib import Path

import pygame

from territory import soundtrack
from territory.client import gamemenu
import territory.client.resources
from territory.client.ui import Client
from territory.server import Server

_DEBUG = 0

# Initialize pygame
pygame.init()

# Path for game's graphics
graphics_root = Path('images')

# Set the icon for the game window
pygame.display.set_icon(pygame.image.load(str(graphics_root / "soldier.png")))

# Generate new random seed
random.seed(round(time.time()))

# Instance of ImageHandler to contain used images in one place
ih = territory.client.resources.ImageHandler()

# Setting Release Version...
conquer_version = "0.2.2"

# Initialize the screen and set resolution
screeni = pygame.display.set_mode((800, 600))

# Set windows caption
pygame.display.set_caption("Territory " + conquer_version)

# Resources are greatly saved with this
pygame.event.set_blocked(pygame.MOUSEMOTION)

# Fill the screen with black color
screeni.fill((0, 0, 0))

# Create the server.
server = Server(Path(path[0]))

# Create the Game Board
# Parameters: pygame screen, image container and game path
client = Client(screeni, ih, Path(path[0]), server)
gb = client.board

# Load interface images
client.load_interface_images()

# Load the other images
client.load_graphics()


# Generate main menu
mainmenu = gamemenu.GameMenu(
    client, ih.gi("menu_interface"), ih.gi("logo"),
    [("Play Scenario", 0, [], "Play a premade map"),
     ("Play Random Island", 1, [], "Generate and play a random map"),
     ("Options", 2, [], "Modify your game experience"),
     ("Map Editor", 3, [], "Edit your own scenario"),
     ("Quit", 4, [], "Exits the program")],
    (800 / 2 - 10, 200),
    settings=client.configuration.skin("menu", {}),
    spacing=60)

# Generate Options menu
optionsmenu = gamemenu.GameMenu(
    client, ih.gi("menu_interface"), ih.gi("logo"),
    [("Show CPU moves with lines", 0,
      ["value_bool_editor", gb.show_cpu_moves_with_lines],
      "(Use left and right arrow key) Show CPU soldiers moves with lines."),
     ("Return", 2, [], None)],
    (800 / 2 - 10, 200), settings=client.configuration.skin("menu", {}),
    spacing=60)

soundtrack.init()

# The true main loop behind the whole application
main_loop_running = True
while main_loop_running:
    # Get selection from main menu
    tulos = mainmenu.get_selection()
    if tulos == 0:

        # Dynamically generate menu items from scenario - files

        # Read scenarios
        scenarios = gb.read_scenarios()

        generated_menu_items = [("Back to Menu", 0, [], None)]

        # Add option to step back to main menu

        # Add scenarios as menuitems
        for i, scenario in enumerate(scenarios):
            generated_menu_items.append((scenario.name, i + 1, [], None))

        # Build the menu
        newgamemenu = gamemenu.GameMenu(
            client, ih.gi("menu_interface"), ih.gi("logo"),
            generated_menu_items, (800 / 2 - 10, 200),
            settings=client.configuration.skin("menu", {}),
            spacing=30)

        # Get selection from the newly build menu
        selection = newgamemenu.get_selection()
        if selection > 0:
            # User selected a scenario
            gb.map_edit_mode = False
            gb.new_game(randommap=False,
                        scenariofile=newgamemenu.menuitems[selection][0])
            gb.start_game()

    # User selected to generate a random map
    elif tulos == 1:
        # Ask player counts
        m1, m2 = client.get_human_and_cpu_count()
        gb.map_edit_mode = False

        # Initialize a new game
        gb.new_game(randommap=True, humanplayers=m1, randomplayers_cpu=m2)

        # Start the game
        gb.start_game()

    # User selected to see options
    elif tulos == 2:
        while True:
            # Get selections from the options menu and break the loop
            # if user wants to get back to the main menu
            tulos2 = optionsmenu.get_selection()
            if tulos2 == 2:
                break

    # User selected to edit a scenario
    elif tulos == 3:
        # FIXME: little better looking
        # Ask player counts
        m1, m2 = client.get_human_and_cpu_count()

        # Fill map with empty space
        gb.fillmap(0)

        # Turn the editing mode on
        gb.playerlist = []
        gb.map_edit_mode = True
        gb.map_edit_info = [m1, m2, 1]
        gb.actors.clear()

        # Start Editing
        gb.start_game()
        # Editing Finished

        gb.map_edit_mode = False
        gb.map_edit_info = []

    # User selected to quit the game
    elif tulos == 4:
        main_loop_running = False
