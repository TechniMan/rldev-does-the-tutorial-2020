#!/usr/bin/env python3
import tcod

from engine import Engine
from entity import Entity
from input_handlers import EventHandler
import colours


def main() -> None:
    # general vars
    screen_width = 80
    screen_height = 50
    # player vars
    player = Entity(
        int(screen_width / 2),
        int(screen_height / 2),
        "@",
        colours.WHITE
    )
    npc = Entity(
        int(screen_width / 2 - 5),
        int(screen_height / 2 - 5),
        "@",
        colours.RED
    )
    entities = { npc, player }

    # init event handler
    event_handler = EventHandler()
    # init engine
    engine = Engine(
        entities=entities,
        event_handler=event_handler,
        player=player
    )

    # load the tileset
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    # set up the context
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True
    ) as context:
        # init console
        root_console = tcod.Console(screen_width, screen_height, order="F")

        # game loop
        while True:
            # handle input from player
            events = tcod.event.wait()
            engine.handle_events(events)

            # print everything to screen
            engine.render(console=root_console, context=context)


if __name__ == "__main__":
    main()
