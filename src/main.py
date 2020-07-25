#!/usr/bin/env python3
import copy
import random
import tcod
import traceback

import colours
from engine import Engine
import entity_factories
from exceptions import Impossible
from procgen import generate_dungeon


def main() -> None:
    # general vars
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 43
    room_min_size = 5
    room_max_size = 10
    max_rooms = 30
    enemies_per_room = (0, 3)
    items_per_room = (0, 2)
    # player vars
    player = copy.deepcopy(entity_factories.player)

    # init engine
    engine = Engine(
        player=player
    )
    # in future, have a data type to hold all these params
    #  for ease of generating different dungeons
    engine.game_map = generate_dungeon(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        enemies_per_room,
        items_per_room,
        engine
    )
    engine.update_fov()

    # choose a random tileset until I can decide which I prefer
    tilesets_available = [
        ("Cheepicus-16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        # ("dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD),
        ("Guybrush-square-16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        ("Kelora-16x16-diagonal.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        ("Moons-square-16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        ("Msgothic.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        ("Tahin-16x16-rounded.png", 16, 16, tcod.tileset.CHARMAP_CP437),
        #("Tigrex3d.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    ]
    chosen_tileset = random.choice(tilesets_available)
    # load the tileset
    tileset = tcod.tileset.load_tilesheet(
        # "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
        "tiles/" + chosen_tileset[0], chosen_tileset[1], chosen_tileset[2], chosen_tileset[3]
    )

    engine.message_log.add_message(
        f"Hello and welcome, adventurer, to yet another dungeon! Tileset: {chosen_tileset[0]}",
        colours.WELCOME_TEXT,
        stack=False
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
            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Impossible as exc:
                engine.message_log.add_message(exc.args[0], colours.IMPOSSIBLE)
            except Exception:
                traceback.print_exc()
                engine.message_log.add_message(traceback.format_exc(), colours.ERROR)

            # print everything to screen
            root_console.clear()
            engine.event_handler.on_render(root_console)
            context.present(root_console)



if __name__ == "__main__":
    main()
