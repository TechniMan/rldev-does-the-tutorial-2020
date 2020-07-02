from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING

import colours

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
        self,
        name: str,
        char: str,
        colour: Tuple[int, int, int],
        x: int = 0,
        y: int = 0,
        blocks_movement: bool = False
    ):
        self.name = name
        self.char = char
        self.colour = colour
        self.x = x
        self.y = y
        self.blocks_movement = blocks_movement

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """ Spawn a copy of this instance at the given location """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        gamemap.entities.add(clone)
        return clone
    
    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
