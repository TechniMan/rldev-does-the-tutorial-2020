from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from actions import EscapeAction, MovementAction
from entity import Entity
from input_handlers import EventHandler
from game_map import GameMap


class Engine:
    def __init__(self,
        entities: Set[Entity],
        event_handler: EventHandler,
        game_map: GameMap,
        player: Entity
    ):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)

    def render(self, console: Console, context: Context) -> None:
        # render the map to the console
        self.game_map.render(console)

        # render entities to the console, on top of the map
        for entity in self.entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.colour)

        # present the console to the screen
        context.present(console)
        # and clear the console ready for the next frame
        console.clear()
