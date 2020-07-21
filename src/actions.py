from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import colours
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """ Return the engine this action belongs to """
        return self.entity.gamemap.engine

    @property
    def target_actor(self) -> Optional[Actor]:
        """ return the actor at this action's destination """
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        """
        Perform this action with the objects needed to determine its scope.
        `self.engine` is the scope this action is being performed in.
        `self.entity` is the object performing the action.
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """ Returns this action's destination """
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """ Return the blocking entity at this action's destination """
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class DropItemAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)
        self.item = item

    def perform(self) -> None:
        self.entity.inventory.drop(self.item)


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class ItemAction(Action):
    def __init__(self,
            entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None):
        super().__init__(entity)
        self.item = item
        # if no target was specified, then target self
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """ Returns the actor at this action's target location """
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """ Invoke the item's ability """
        self.item.consumable.activate(self)


class PickupAction(Action):
    """ Picks up the first item on the floor beneath the actor """
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            # find the item which is in the same location as the actor
            if item.x == actor_location_x and item.y == actor_location_y:
                if inventory.is_full:
                    raise exceptions.Impossible(f"Your inventory is too full to pick up the {item.name}!")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.add(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}.")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class WaitAction(Action):
    def perform(self):
        pass


class MeléeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        # if there isn't an actor there, then quit early
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense
        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_colour = colours.PLAYER_ATTACK
        else:
            attack_colour = colours.ENEMY_ATTACK

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_description} for {damage} hit points",
                attack_colour
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_description}, but does no damage.",
                attack_colour
            )


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        # if entity is trying to move out of bounds, don't move
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("The way is shut.")
        # if entity is trying to walk into an unwalkable tile (e.g. a wall), don't move
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("The way is shut.")
        # if entity is trying to walk into a movement-blocking entity, don't move
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("The way is shut.")

        # finally, move the entity
        self.entity.move(self.dx, self.dy)


# Attempts to move into a space, otherwise deals with whatever's in the way
class BumpAction(ActionWithDirection):
    """ Attempts to move into a space, otherwise deals with whatever's in the way """
    def perform(self) -> None:
        if self.target_actor:
            return MeléeAction(self.entity, self.dx, self.dy).perform()
        # otherwise, move into the empty space
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
