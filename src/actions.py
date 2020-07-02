from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """
        Perform this action with the objects needed to determine its scope.
        `engine` is the scope this action is being performed in.
        `entity` is the object performing the action.
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class ActionWithDirection(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class MovementAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # if entity is trying to move out of bounds, don't move
        if not engine.game_map.in_bounds(dest_x, dest_y):
            return
        # if entity is trying to walk into an unwalkable tile (e.g. a wall), don't move
        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        # if entity is trying to walk into a movement-blocking entity, don't move
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return

        # finally, move the entity
        entity.move(self.dx, self.dy)


class MeléeAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
        if not target:
            return

        print(f"You kick the {target.name}, much to its annoyance!")


# Attempts to move into a space, otherwise deals with whatever's in the way
class BumpAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        # if would move into a blocking entity, attempt to attack it instead
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return MeléeAction(self.dx, self.dy).perform(engine, entity)
        # otherwise, move into the empty space
        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)
