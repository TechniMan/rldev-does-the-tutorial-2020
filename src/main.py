#!/usr/bin/env python3
import tcod

from actions import EscapeAction, MovementAction
from input_handlers import EventHandler


def main() -> None:
    # general vars
    screen_width = 80
    screen_height = 50
    # player vars
    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

    # load the tileset
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    # init event handler
    event_handler = EventHandler()

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
            # await input from player
            for event in tcod.event.wait():
                action = event_handler.dispatch(event)

                if action is None:
                    continue

                if isinstance(action, MovementAction):
                    player_x += action.dx
                    player_y += action.dy

                elif isinstance(action, EscapeAction):
                    raise SystemExit()

            # clear the console before we print to it
            root_console.clear()

            # print our player
            root_console.print(x=player_x, y=player_y, string="@")

            # present everything we've printed to the screen
            context.present(root_console)


if __name__ == "__main__":
    main()
