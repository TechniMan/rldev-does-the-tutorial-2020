from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """ Return the engine this action belongs to """
        return self.entity.game_map.engine

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


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class WaitAction(Action):
    def perform(self):
        pass


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        # if entity is trying to move out of bounds, don't move
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        # if entity is trying to walk into an unwalkable tile (e.g. a wall), don't move
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        # if entity is trying to walk into a movement-blocking entity, don't move
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return

        # finally, move the entity
        self.entity.move(self.dx, self.dy)


class MeléeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return

        damage = self.entity.fighter.power - target.fighter.defense
        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"
        if damage > 0:
            print(f"{attack_description} for {damage} hit points")
            target.fighter.hp -= damage
        else:
            print(f"{attack_description} but does no damage!")

        print(f"You kick the {target.name}, much to its annoyance!")


# Attempts to move into a space, otherwise deals with whatever's in the way
class BumpAction(ActionWithDirection):
    """ Attempts to move into a space, otherwise deals with whatever's in the way """
    def perform(self) -> None:
        if self.target_actor:
            return MeléeAction(self.entity, self.dx, self.dy).perform()
        # otherwise, move into the empty space
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
