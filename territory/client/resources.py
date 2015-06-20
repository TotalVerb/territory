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


class ImageHandler:
    """Simple image container."""

    def __init__(self):
        self.images = {}

    def add_image(self, image, id):
        self.images[id] = image

    # Get Image
    def gi(self, id):
        return self.images.get(id, None)


pygame.font.init()
font1 = pygame.font.Font(None, 12)
font2 = pygame.font.Font(None, 16)
font3 = pygame.font.Font(None, 24)
font4 = pygame.font.Font("fonts/AveriaSerif-Regular.ttf", 20)
mono_font = pygame.font.Font("fonts/ConsolaMono-Bold.ttf", 17)
