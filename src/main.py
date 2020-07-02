#!/usr/bin/env python3
import copy

import tcod

import colours
from engine import Engine
from entity import Entity
import entity_factories
from input_handlers import EventHandler
from procgen import generate_dungeon


def main() -> None:
    # general vars
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    room_min_size = 5
    room_max_size = 10
    max_rooms = 30
    enemies_per_room = (0, 2)
    # player vars
    player = copy.deepcopy(entity_factories.player)

    # in future, have a data type to hold all these
    #  for ease of generating different dungeons
    game_map = generate_dungeon(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        enemies_per_room,
        player
    )

    # init event handler
    event_handler = EventHandler()
    # init engine
    engine = Engine(
        event_handler=event_handler,
        game_map=game_map,
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
