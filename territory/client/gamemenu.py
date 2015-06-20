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

import pygame


class GameMenu:
    def __init__(self, client, bg_image, logo1, menuitems, start_xy, settings,
                 spacing=50):
        # Currently selected menuitem's index
        self.item_index = 0
        # List of menuitems
        self.menuitems = menuitems
        # Pointer to pygame screen
        self.client = client
        # Font to be used with the menu
        self.used_font = pygame.font.Font("fonts/AveriaSerif-Regular.ttf", 24)
        # Coordinates where to render the menu
        self.start_x, self.start_y = start_xy
        # Space between menuitems
        self.spacing = spacing
        # Background picture is oddly here as well the top logo
        self.menukuva = bg_image
        self.logo = logo1
        # New style settings
        self.settings = settings

    def draw_items(self, text=None):
        # If images and/or text are supplied, draw them
        if self.menukuva:
            self.client.screen.blit(self.menukuva, (0, 0))
        if self.logo:
            self.client.screen.blit(self.logo, (263, 0))
        if text:
            self.client.text_at(
                text[0], (text[1], text[2]), font=self.used_font,
                wipe_background=True, color=(255, 255, 255), centre=True
            )

        # Iterate through menu items
        for i, item in enumerate(self.menuitems):
            # FIXME: skinnable colors

            # Menu item color; get from settings
            colour = self.settings.get("item_colour_default", (0, 0, 0))
            shadow = False
            if i == self.item_index:
                # Selected menu item is red
                shadow = False
                colour = self.settings.get("item_colour_selected", (255, 0, 0))

            # Text to be rendered
            text = item[0]

            # Check if menu items are value editors
            if len(item[2]) >= 2:
                if item[2][0] == "value_int_editor":
                    text = "%s (%d)" % (text, item[2][1])
                elif item[2][0] == "value_bool_editor":
                    if item[2][1]:
                        text = "%s (%s)" % (text, "on")
                    else:
                        text = "%s (%s)" % (text, "off")
                elif item[2][0] == "value_str_editor":
                    text = "%s (%s)" % (text, item[2][1])

            # Draw the menu item text
            self.client.text_at(
                text, (self.start_x, self.start_y + self.spacing * i),
                font=self.used_font, color=colour, wipe_background=False,
                drop_shadow=shadow, centre=True)

        # Caption Text
        if self.menuitems[self.item_index][3]:
            # It has caption text, draw it
            self.client.text_at(
                self.menuitems[self.item_index][3], (400, 75),
                font=self.used_font, centre=True)

        # Some info :)
        self.client.text_at(
            "Territory https://github.com/TotalVerb/territory/",
            (400, 545), font=self.used_font, color=(0, 0, 0),
            wipe_background=False, centre=True
        )

    def rullaa(self, dy):
        # Change the selected menu item
        self.item_index += dy
        self.item_index %= len(self.menuitems)

    def edit_value(self, dv):
        # This is totally unreadable :D
        # Well it edits values in their border values
        item = self.menuitems[self.item_index][2]
        if len(item) >= 2:
            if item[0] == "value_int_editor":
                item[1] += dv
                if len(item) >= 3:
                    if item[1] < item[2][0]:
                        item[1] = item[2][0]
                    if item[1] > item[2][1]:
                        item[1] = item[2][1]
            if item[0] == "value_bool_editor":
                item[1] = not item[1]

    def get_selection(self, text=None):
        """Render the menu as long as user selects a menuitem

        :param text: optional text to be rendered
        """

        # Draw the items
        self.draw_items(text)

        # Create instance of pygame Clock
        clock = pygame.time.Clock()

        # Endless loop
        while True:

            # Limit fps to 30
            clock.tick(30)

            # Iterate through events
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_DOWN:
                        self.rullaa(1)
                        self.draw_items(text)
                    if e.key == pygame.K_UP:
                        self.rullaa(-1)
                        self.draw_items(text)
                    if e.key == pygame.K_RETURN:
                        tulos = self.select()
                        return tulos
                    if e.key == pygame.K_LEFT:
                        self.edit_value(-1)
                        self.draw_items(text)
                    if e.key == pygame.K_RIGHT:
                        self.edit_value(1)
                        self.draw_items(text)
            pygame.display.flip()

    def select(self):
        # User selects a menu item
        return self.menuitems[self.item_index][1]
