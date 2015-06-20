# Changelog

## 0.2.2

 * Introduced Python 3 support. Dropped Python 2 support.
 * Gameplay changes:
    - When islands merge, the new dump location is where the biggest dump was
      instead of being randomly generated.
    - (Default ruleset) Units can now be merged. If a friendly unit moves over
      another, then the levels of both are summed.
    - (Default ruleset) Buying a soldier now costs 2 supplies instead of one.
      This leads to more strategic games, because the value of a soldier is
      higher.
 * Configuration enhancements:
    - New ruleset functionality: Classic (maintains original conquer behaviour
      where reasonable), Slay (behaves more like Slay), and Default (newest
      features always available on this ruleset).
 * UI enhancements:
    - AI lines last a bit longer
    - Brief pause if at least one unit died
    - Scoreboard updates more often
 * Cleanup of backend code (still in progress).
 * Changes to images and fonts of default skin.
 * Updated CPU player names.
 * Bug fixes:
    - CPU players can no longer have duplicate names.
    - Fixed problem where off-screen units do not die from lack of supplies.
    - Fixed impossibility of typing uppercase letters or punctuation that
      requires pressing the shift key.

## 0.2.1
 * Added music
    - Soundtrack: for menu and game
    - Sound effects: Death, Destruction, Upgrade unit, Victory
 * Default skin changes:
    - Added new variable unit images (use UnitImage settings)
    - Cleaned up some images
    - New menu image that is kinder to the eye
 * Configuration enhancements:
    - Menu logo image: the logo
    - Menu logofolder folder: where the logo is stored
    - Enabled comments in cpu_player_names
    - Menu item_colour_default
    - Menu item_colour_selected
    - Allowed skinning of hextile graphics
    - Allowed skinning of mapedit background
    - Removed interface_filename option (use ScreenBg gameboard)
 * Added support for options.ini (imported from Conquer)
    - Change skin
    - Default lines
    - Default recursion depth
 * Default skin changes:
    - New background for gameplay
    - New background for map editor
    - New text selection colours
 * Changed default CPU player names
 * Added descriptive text for Options and Quit
 * Made scenario listing ignore hidden and backup files

## 0.2

Forked from Conquer project.