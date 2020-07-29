from __future__ import annotations

import numpy
import random
import tcod
from typing import List, Optional, Tuple, TYPE_CHECKING

from actions import Action, BumpAction, MeléeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """
        Returns a path to the target position.
        If there is no valid path, returns an empty list.
        """
        # copy the walkable tiles
        cost = numpy.array(self.entity.gamemap.tiles["walkable"], dtype=numpy.int8)

        # for each entity in the map
        #  if it is blocking movement
        #   add to the cost of that tile for pathfinding
        for entity in self.entity.gamemap.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] += 10

        # create walkable graph based on the cost array
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=1, diagonal=2)
        # the pathfinder will find the path :thumbsup:
        pathfinder = tcod.path.Pathfinder(graph)

        # set starting position
        pathfinder.add_root((self.entity.x, self.entity.y))
        # get the path to the destination
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # convert from List[List[int]] to List[Tuple[int, int]]
        return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """ A confused enemy will stumble around for a specified time then return to its previous behaviour.
    If an actor occupies the tile it is randomly moving into, it will attack them. """
    def __init__(self,
        entity: Actor, previous_ai: Optional[BaseAI], turns: int
    ):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns

    def perform(self) -> None:
        # when the timer runs out, reset the behaviour
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
        else:
            # otherwise, pick a random direction and move or attack whatever's there
            x, y = random.choice([
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ])
            self.turns_remaining -= 1
            return BumpAction(self.entity, x, y).perform()


class HostileEnemy(BaseAI):
    def __init__(self,
        entity: Actor
    ):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        # Chebyshev distance https://en.wikipedia.org/wiki/Chebyshev_distance
        distance = max(abs(dx), abs(dy))

        # if our location is visible (to the player)
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            # if we are within melée range, 'it 'em
            if distance <= 1:
                return MeléeAction(self.entity, dx, dy).perform()
            # else find the path towards the player so we can 'it 'em
            self.path = self.get_path_to(target.x, target.y)

        # if we want to move somewhere
        if self.path:
            # move to the first tile along our path
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y
            ).perform()

        # otherwise, stand around and wait for something to happen
        return WaitAction(self.entity).perform()
