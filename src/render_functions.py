from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

import colours

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


def render_bar(
    console: Console,
    position: Tuple[int, int],
    current_value: int,
    maximum_value: int,
    total_width: int
) -> None:
    bar_width = int((float(current_value) / float(maximum_value)) * float(total_width))
    # draw the bar background
    console.draw_rect(position[0], position[1], total_width, 1, 1, bg=colours.BAR_EMPTY)

    # if necessary, draw the bar foreground
    if bar_width > 0:
        console.draw_rect(position[0], position[1], bar_width, 1, 1, bg=colours.BAR_FILLED)

    # draw bar text
    console.print(position[0] + 1, position[1], f"HP: {current_value} / {maximum_value}", colours.BAR_TEXT)


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )
    return names.capitalize()


def render_names_at_mouse_position(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_position
    names = get_names_at_location(mouse_x, mouse_y, engine.game_map)
    console.print(x, y, names, colours.GENERAL_TEXT)
