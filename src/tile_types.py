from typing import Tuple

import numpy # type: ignore

import colours


# Helper datatypes for tcod Console to understand our tile data

# Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = numpy.dtype(
    [
        ("ch", numpy.int32), # Unicode codepoint
        ("fg", "3B"),        # 3 unsigned bytes, for RGB colours
        ("bg", "3B")
    ]
)

# Tile struct used for statically defined tile data
tile_dt = numpy.dtype(
    [
        ("walkable", numpy.bool),    # True if this tile can be walked on by entities
        ("transparent", numpy.bool), # True if this entity doesn't block line of sight
        ("unlit", graphic_dt),        # Graphic data for when this tile is not in FOV
        ("lit", graphic_dt)        # Graphic data for when this tile is in FOV
    ]
)


# Helper to define tile types in a way tcod Console will understand
def new_tile(
    *, # Enforce the use of keywords, so that parameter order doesn't matter
    walkable: int,
    transparent: int,
    unlit: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    lit: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
) -> numpy.ndarray:
    """ Helper function for defining individual tile types """
    return numpy.array((walkable, transparent, unlit, lit), dtype=tile_dt)


# FOG: default, for unseen tiles
FOG = numpy.array((ord(" "), colours.FOG, colours.BLACK), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    unlit=(ord("."), colours.GROUND_UNLIT, colours.BLACK),
    lit=(ord("."), colours.GROUND_LIT, colours.BLACK)
)
wall = new_tile(
    walkable=False,
    transparent=False,
    unlit=(ord("#"), colours.WALL_UNLIT, colours.BLACK),
    lit=(ord("#"), colours.WALL_UNLIT, colours.BLACK)
)
