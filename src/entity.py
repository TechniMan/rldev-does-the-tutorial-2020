from __future__ import annotations

import copy
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING

import colours

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    game_map: GameMap

    def __init__(
        self,
        name: str,
        char: str,
        colour: Tuple[int, int, int],
        x: int = 0,
        y: int = 0,
        blocks_movement: bool = False,
        gamemap: Optional[GameMap] = None
    ):
        self.name = name
        self.char = char
        self.colour = colour
        self.x = x
        self.y = y
        self.blocks_movement = blocks_movement
        # if gamemap isn't provided now, then it will be set later
        if gamemap:
            self.game_map = gamemap
            gamemap.entities.add(self)

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """ Spawn a copy of this instance at the given location """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.game_map = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """ Place this entity at a new location. Handles movement across game maps. """
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "game_map"):
                self.game_map.entities.remove(self)
            self.game_map = gamemap
            gamemap.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
