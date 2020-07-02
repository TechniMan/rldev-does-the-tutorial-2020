import numpy # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = numpy.full((width, height), fill_value=tile_types.wall, order="F")
        self.visible = numpy.full((width, height), fill_value=False, order="F")
        self.explored = numpy.full((width, height), False, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        """ Returns True if x and y are inside of the bounds of this map """
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.
        Visible tiles are drawn with their "lit" colour.
        Explored tiles are drawn with their "unlit" colour.
        Other tiles are drawn as FOG.
        """
        # pass the map tile colours to the console
        console.tiles_rgb[0:self.width, 0:self.height] = numpy.select(
            [self.visible, self.explored],
            [self.tiles["lit"], self.tiles["unlit"]],
            tile_types.FOG
        )
