import numpy # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = numpy.full((width, height), fill_value=tile_types.floor, order="F")
        # initialise some tiles as walls
        self.tiles[30:33, 22] = tile_types.wall

    def in_bounds(self, x: int, y: int) -> bool:
        """ Returns True if x and y are inside of the bounds of this map """
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        # pass the map tile colours to the console
        console.tiles_rgb[0:self.width, 0:self.height] = self.tiles["dark"]
