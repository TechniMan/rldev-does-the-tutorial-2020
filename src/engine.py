from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar, render_names_at_mouse_position

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self,
        player: Actor
    ):
        self.player = player
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_position = (0, 0)

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    # ignore impossible action exceptions
                    pass

    def update_fov(self) -> None:
        """ Recompute the visible area based on the player's point of view """
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            8
        )
        # if a tile has become visible, mark it also as explored
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        # render the map to the console, offset to keep the player centred
        cam_x, cam_y = self.offset_coordinates(0, 0)
        self.game_map.render(console, cam_x, cam_y)

        self.message_log.render(console, 21, 45, 40, 5)

        render_bar(console, (1, 45), self.player.fighter.hp, self.player.fighter.max_hp, 20)
        render_names_at_mouse_position(console, 21, 44, self)

    def offset_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """ Offset the given co-ordinates for rendering
            Offset puts player at the centre of the screen """
        return (
            int(self.game_map.render_width / 2) - self.player.x + x,
            int(self.game_map.render_height / 2) - self.player.y + y
        )
