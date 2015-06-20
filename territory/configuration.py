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
import configparser

NO_DEFAULT = object()


class ConfigurationManager:
    """A storage for configuration (skin, settings, etc.)."""

    def __init__(self):
        self.skin_name = "default"
        self.sc = {}

        # Misc options
        self.ai_recursion_depth = None
        self.show_cpu_moves = None
        self.ruleset = None

        # Load the options file
        self.ini_options = configparser.RawConfigParser()
        self.load_options_file("options.ini")

        # Load the skin configuration file
        self.load_skin_file("skins/{}".format(self.skin_name))

    def skin(self, option, default=NO_DEFAULT):
        *hierarchy, last = option.split('.')
        current = self.sc
        for layer in hierarchy:
            current = current.get(layer, {})

        if default is not NO_DEFAULT:
            return current.get(last, default)
        else:
            return current[last]

    def load_options_file(self, file):
        self.ini_options.read(file)
        # Set our settings
        self.skin_name = self.ini_options.get("MainConf", "skin")
        self.ai_recursion_depth = int(
            self.ini_options.get("MainConf", "cpu_recursion_depth"))
        self.show_cpu_moves = self.ini_options.get("MainConf",
                                                   "cpu_movesl") == "true"
        self.ruleset = self.ini_options.get("MainConf", "ruleset")

    def load_skin_file(self, filename1):
        """Load skin configuration file and read it into sc."""

        file = open(filename1, "r")
        for line in file:
            line = line.strip()
            if not line:
                # Empty line, go to next
                continue
            else:
                if line[0] == "#":
                    # Line is comment, go to next line
                    continue

            # Copy the line, pretty useless expression
            rivi = line

            # Make lowercase and split
            rivi = rivi.lower()
            rivi = rivi.split(" ")

            # Configuration options into sc, read the skin file for more info
            if rivi[0] == "unit_status_text_topleft_corner":
                self.sc["unit_status_text_topleft_corner"] = (
                    int(rivi[1]), int(rivi[2]))
            elif rivi[0] == "scoreboard_text_topleft_corner":
                self.sc["scoreboard_text_topleft_corner"] = (
                    int(rivi[1]), int(rivi[2]))
            elif rivi[0] == "unit_status_text_color":
                self.sc["unit_status_text_color"] = (
                    int(rivi[1]), int(rivi[2]), int(rivi[3]))
            elif rivi[0] == "scoreboard_text_color":
                self.sc["scoreboard_text_color"] = (
                    int(rivi[1]), int(rivi[2]), int(rivi[3]))
            elif rivi[0] == "button_endturn":
                self.sc["button_endturn"] = (
                    (int(rivi[1]), int(rivi[2])), (int(rivi[3]), int(rivi[4])))
            elif rivi[0] == "button_quit":
                self.sc["button_quit"] = (
                    (int(rivi[1]), int(rivi[2])), (int(rivi[3]), int(rivi[4])))
            elif rivi[0] == "making_moves_text_topleft_corner":
                self.sc["making_moves_text_topleft_corner"] = (
                    int(rivi[1]), int(rivi[2]))
            elif rivi[0] == "menu_interface_filename":
                self.sc["menu_interface_filename"] = rivi[1]
            elif rivi[0] == "making_moves_text_color":
                self.sc["making_moves_text_color"] = (
                    int(rivi[1]), int(rivi[2]), int(rivi[3]))

            # New-style lines do not follow a set formula
            else:
                params = rivi[2:]
                paramsc = []
                if rivi[0] not in self.sc:
                    self.sc[rivi[0]] = dict()
                for i in params:
                    try:
                        paramsc.append(int(i))  # Assume integer
                    except ValueError:
                        paramsc.append(i)  # String as contingency plan
                self.sc[rivi[0]][rivi[1]] = tuple(paramsc)
