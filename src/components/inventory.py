from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent
import exceptions

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    @property
    def count(self) -> int:
        return len(self.items)

    def add(self, item: Item) -> None:
        """ Attempts to add an item to the inventory,
        raising Impossible is it is full. """
        if self.is_full:
            raise exceptions.Impossible("Your inventory is full.")
        self.items.append(item)

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map 
         at the parent entity's current location
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")
