from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from input_handlers import EventHandler
from game_map import GameMap

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap


class Engine:
    game_map: GameMap

    def __init__(self,
        player: Entity
    ):
        self.event_handler = EventHandler(self)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f'The {entity.name} wonders when it will get to take a real turn.')

    def update_fov(self) -> None:
        """ Recompute the visible area based on the player's point of view """
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            8
        )
        # if a tile has become visible, mark it also as explored
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        # render the map to the console
        self.game_map.render(console)

        # present the console to the screen
        context.present(console)
        # and clear the console ready for the next frame
        console.clear()
