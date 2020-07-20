from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor

class Fighter(BaseComponent):
    parent: Actor

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
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def heal(self, amount: int) -> int:
        """ Adds `amount` to hp, and returns the amount healed """
        if self.hp == self.max_hp:
            return 0

        # don't overheal :)
        new_hp_value = self.hp + amount
        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        # figure out the difference before we change it
        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        return amount_recovered

    def take_true_damage(self, amount: int) -> None:
        self.hp -= amount

    def take_physical_damage(self, amount: int) -> None:
        if amount > self.defense:
            self.hp -= (amount - self.defense)

    def die(self) -> None:
        # if we are the player
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_colour = colours.PLAYER_DIE
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.parent.name} has died"
            death_message_colour = colours.ENEMY_DIE

        self.parent.render_order = RenderOrder.CORPSE
        self.parent.char = "%"
        self.parent.colour = colours.DEAD
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"

        self.engine.message_log.add_message(death_message, death_message_colour)
