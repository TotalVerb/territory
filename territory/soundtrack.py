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

from sys import path
from pathlib import Path

import pygame.mixer

pygame.mixer.init()

# Initialize our channels

soundtrack = pygame.mixer.Channel(0)
sfx = pygame.mixer.Channel(1)

# Directories
# TODO: Allow sound skins
sound_dir = Path(path[0]) / "music"

# Get our sounds
# TODO: Allow sound skins

soundtracks = {}
sfxs = {}


def register_sfx(name, loc=None):
    if not loc:
        loc = name + ".ogg"
    sfxs[name] = pygame.mixer.Sound(str(sound_dir / loc))


def register_soundtrack(name, loc=None):
    if not loc:
        loc = name + ".ogg"
    soundtracks[name] = pygame.mixer.Sound(str(sound_dir / loc))

# TODO: move elsewhere
register_sfx("destroy")
register_sfx("die")
register_sfx("upgrade")
register_sfx("victory")

register_soundtrack("soundtrack")
register_soundtrack("march")


def play_sfx(name):
    if name in sfxs:
        if sfx.get_busy():
            sfx.stop()
        sfx.play(sfxs[name])
    else:
        pass  # maybe do something?


def init():
    soundtrack.play(soundtracks["soundtrack"], loops=-1)


def play_soundtrack(name):
    if name in soundtracks:
        # TODO: fade out music
        soundtrack.stop()
        soundtrack.play(soundtracks[name], loops=-1)
    else:
        pass
