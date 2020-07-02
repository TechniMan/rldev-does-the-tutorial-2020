from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
from entity import Entity
from input_handlers import EventHandler
from game_map import GameMap


class Engine:
    def __init__(self,
        event_handler: EventHandler,
        game_map: GameMap,
        player: Entity
    ):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f'The {entity.name} wonders when it will get to take a real turn.')

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            # attempt to perform the player's action
            action.perform(self, self.player)
            # give the enemies a turn
            self.handle_enemy_turns()
            # update the field of view after the player has acted
            self.update_fov()

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
