from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import colours
from components.base_component import BaseComponent
from components.inventory import Inventory
import exceptions

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """ Try to return the action for this item """
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemACtion) -> None:
        """
        Invoke this item's ability
        `action` is the context for this activation
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """ Removes the consumed item from its containing inventory """
        item = self.parent
        inventory = item.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(item)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        # attempt to heal the consumer
        amount_recovered = action.entity.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name} and recovered {amount_recovered} HP.",
                colours.HEALTH_RECOVERED
            )
            self.consume()
        else:
            raise exceptions.Impossible("Your health is already full.")
