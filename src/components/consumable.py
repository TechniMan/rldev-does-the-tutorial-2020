from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import colours
import components.base_component
import exceptions
from input_handlers import AreaRangedAttackHandler, SingleRangedAttackHandler

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(components.base_component.BaseComponent):
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
        if isinstance(inventory, components.inventory.Inventory):
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


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lightning bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_true_damage(self.damage)
            self.consume()
        else:
            raise exceptions.Impossible("No enemies within range.")


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message("Select a target location", colours.NEEDS_TARGET)
        self.engine.event_handler = SingleRangedAttackHandler(self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy)
        )
        return None

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise exceptions.Impossible("You cannot target an area that you cannot see!")
        if not target:
            raise exceptions.Impossible("You must select an enemy to target!")
        if target is consumer:
            raise exceptions.Impossible("You cannot cast this upon yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around.",
            colours.STATUS_EFFECT_APPLIED
        )
        target.ai = components.ai.ConfusedEnemy(
            target, target.ai, self.number_of_turns
        )
        self.consume()


class FireballConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location", colours.NEEDS_TARGET
        )
        self.engine.event_handler = AreaRangedAttackHandler(
            self.engine,
            self.radius,
            lambda xy: actions.ItemAction(consumer, self.parent, xy)
        )
        return None

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise exceptions.Impossible("You cannot target an area that you cannot see!")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_true_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise exceptions.Impossible("There are no valid targets in the targeted area.")
        self.consume()
