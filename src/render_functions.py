from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

import colours

if TYPE_CHECKING:
    from tcod import Console


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
