from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class Fighter(BaseComponent):
    entity: Actor

    def __init__(self,
        hp: int,
        defense: int,
        power: int
    ):
        """
        `hp` is the entity's maximum hit points
        `defense` is subtracted from the damage the entity takes
        `power` is the damage the entity deals to others
        """
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        # this ensures that hp can never be lower than 0 or greater than `max_hp`
        self._hp = (max(0, min(value, self.max_hp)))
        if self._hp <= 0 and self.entity.ai:
            self.die()

    def die(self) -> None:
        # if we are the player
        if self.engine.player is self.entity:
            death_message = "You died!"
        else:
            death_message = f"{self.entity.name} has died"

        self.entity.char = "%"
        self.entity.colour = colours.RED
        self.entity.blocks_movement = False
        self.entity.ai = None
        self.entity.name = f"remains of {self.entity.name}"

        print(death_message)