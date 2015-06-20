# Territory manual

The goal in Territory is to eliminate enemy players.

## Island

An <q>island</q> is a group of two or more same-colored lands that are
connected. Every island has its own resource dump. When two islands merge into
one larger island, old supplies from the smaller dumps are brought and added to
the biggest dump from the two old ones (which are then discarded). The ultimate
goal of the game is to eliminate all enemy islands.

## Units

### Resource Dump

Your island's base of action. Resource Dump supply income equals
to its islands land area. Islands soldiers levels are added to
expends. Every turn resource dump supplies are changed by following
amount: income - expenses. If supplies drop to zero or below, every
soldier on the island is killed (a skull is drawn briefly). If
resource dump is isolated on one land piece, it is discarded. If
resource dump is conquered by enemy soldier, a new one is created
at random location on the island but with zero supplies.

### Soldier

This is the unit that conquers land. It has 6 power levels.
(1 being the weakest and 6 the strongest)

Rules concerning soldiers:

- Soldier can't conquer land which:

    * is defended by stronger soldier
    (meaning the land does not have stronger enemy
    soldier next to it)
    * has own unit
    * is out of reach from your island

- If a resource dump or soldier is isolated on one land piece,
  it is terminated next turn

- Defending: to have a soldier next to a land piece or resource
             dump to defend it

- Upgrading: Right click to upgrade a soldier one level (costs supplies)
- Upgrading: OR merge soldiers by moving one on top of another... if combined
  levels are not greater than 6!

Soldiers level 1:
    Can't conquer resource dumps or lands that an resource dump
    defends. Also can't attack soldiers whose level is equal or
    greater or conquer lands which are defended by soldiers whose
    level is equal or greater.

Soldiers level 2-5:
    Can't attack soldiers whose level is equal or greater or
    conquer lands which are defended by soldiers whose level is
    equal or greater.

Soldiers level 6:
    Can conquer any reachable land. Attacking another level 6
    soldier has 50% chance of winning or getting killed.

## Interface
- Red box shows selected soldier
- Number of Resource Dump = its supplies
- Number on a soldier tells its level
- X next to level number tell that soldier has moved this turn
- Mouse:
    * Left Click:
        * Select anywhere with soldier selected:
            Selected soldier tries to attack clicked land.
        * Select Soldier:
            Soldier is selected
        * Select Resource Dump:
            Data is shown
    * Right Click: Draft or upgrade soldiers
        * Draft:
            If resource dump on island has supplies, you may
            right click on an empty land to train soldier. The cost to train a
            soldier is 2 supplies.
        * Upgrade:
            If resource dump on island has supplies, you may
            right click on existing soldier to increase its
            level. The cost to upgrade a soldier is 2 supplies. Be careful!
            Upgraded soldiers cost more in upkeep.
- Keyboard:
    * e -> end turn
    * Left Arrow -> scroll map left
    * Right Arrow -> scroll map right
    * Show your units that can move
    * (map editor) Up/Down -> Change player
- Skull drawn on soldier means the soldier was killed because lack
  of supplies on island.
- Green circle shows what/who is blocking move you tried to execute

Have fun!
