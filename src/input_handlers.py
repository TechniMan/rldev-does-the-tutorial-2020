from __future__ import annotations

import tcod
import tcod.console
import tcod.event
from typing import Callable, Optional, Tuple, TYPE_CHECKING

from actions import (
    Action,
    BumpAction,
    DropItemAction,
    EscapeAction,
    PickupAction,
    WaitAction
)
import colours
import exceptions
from entity import Item

if TYPE_CHECKING:
    from engine import Engine


MOVE_KEYS = {
    # numpad keys
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys; may be deprecated later in favour of other functionality for the letters
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_SPACE
}

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -5,
    tcod.event.K_PAGEDOWN: 5
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> bool:
        """ Handle action returned from event methods
        Returns True if the action will advance a turn
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], colours.IMPOSSIBLE)
            return False

        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_mousemotion(self, event: tcod.context.Context) -> None:
        # only update the mouse position if it's within the bounds of the map
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_position = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        # if a key isn't pressed, return None by default
        action: Optional[Action] = None

        # get the `sym`bol pressed by the player
        key = event.sym
        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            items = self.engine.game_map.get_items_at_location(player.x, player.y)
            if len(items) == 0:
                raise exceptions.Impossible("There is nothing here to pick up.")
            elif len(items) == 1:
                action = PickupAction(player, items[0])
            else:
                self.engine.event_handler = ItemPickupHandler(self.engine)
        elif key == tcod.event.K_i:
            self.engine.event_handler = InventoryUseHandler(self.engine)
        elif key == tcod.event.K_d:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            self.engine.event_handler = LookHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()


class HistoryViewer(EventHandler):
    """ Print the history on a larger window which can be scrolled """
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        # draw the main state as the background
        super().on_render(console)
        log_console = tcod.Console(console.width - 6, console.height - 6)

        # draw a frame with a custom banner title
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # render the message log using the cursor
        self.engine.message_log.render_messages(
            log_console, 1, 1, log_console.width - 2, log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1]
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown):
        # fancy conditional movement to make it feel right
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # only move from the top to the bottom when you're on the edge
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                # otherwise move while staying clamped to the bounds of the history log
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            # move directly to the top message
            self.cursor = 0
        elif event.sym == tcod.event.K_END:
            # move directly to the last message
            self.cursor = self.log_length - 1
        else:
            # any other key returns to the normal game state
            self.engine.event_handler = MainGameEventHandler(self.engine)


class AskUserEventHandler(EventHandler):
    """ Handles user input for actions which require special input """
    def handle_action(self, action: Optional[Action]) -> bool:
        """ Return to the main event handler when a valid action was performed """
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """ By default, any key (except modifier keys) will exit this input handler """
        if event.sym in {
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """ By default any mouse click will exit this input handler """
        return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        """ Return to the main game event handler """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler):
    """ This handler lets user select an item from a window """
    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an inventory menu, displaying all items in the inventory
         with the letter to select it.
        Displays in a different position so the player character is always visible.
        """
        super().on_render(console)
        count_of_items = self.engine.player.inventory.count
        height = count_of_items + 2
        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(x = x, y = y, width = width, height = height, title = self.TITLE,
                clear = True, fg = colours.FRAME, bg = colours.BACKGROUND
        )

        if count_of_items > 0:
            for idx, item in enumerate(self.engine.player.inventory.items):
                key = chr(ord("a") + idx)
                console.print(x + 1, y + idx + 1, f"({key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", colours.INVALID)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[Action]:
        raise NotImplementedError()


class InventoryUseHandler(InventoryEventHandler):
    """ Handles using an inventory item """
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """ Return the action for the selected item """
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """ Handles dropping an inventory item """
    TITLE = "Select an item to drop "

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """ Drop the selected item """
        return DropItemAction(self.engine.player, item)


class ItemPickupHandler(AskUserEventHandler):
    """ Handles selecting from multiple items to pick up """
    TITLE = "Select an item to pick up"

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an inventory menu, displaying all items underneath the player.
        Displays in a different position so the player character is always visible.
        """
        super().on_render(console)
        player_x, player_y = self.engine.player.x, self.engine.player.y
        items = self.engine.game_map.get_items_at_location(player_x, player_y)
        height = len(items) + 2
        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(x = x, y = y, width = width, height = height, title = self.TITLE,
                clear = True, fg = colours.FRAME, bg = colours.BACKGROUND
        )

        if len(items) > 0:
            for idx, item in enumerate(items):
                key = chr(ord("a") + idx)
                console.print(x + 1, y + idx + 1, f"({key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a
        items = player.gamemap.get_items_at_location(player.x, player.y)

        if 0 <= index <= 26:
            try:
                selected_item = items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", colours.INVALID)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[Action]:
        return PickupAction(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """ Handles asking the user for an index on the map """
    def __init__(self, engine: Engine):
        """ Initialises the cursor to the player position """
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """ Highlight the tile under the mouse cursor """
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = colours.HIGHLIGHT_BACKGROUND
        console.tiles_rgb["fg"][x, y] = colours.HIGHLIGHT_FOREGROUND

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """ Checks for key movement or confirmation keys """
        key = event.sym
        if key in MOVE_KEYS:
            # amount to speed up movement when holding down modifier keys
            cursor_speed = 1
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                cursor_speed *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                cursor_speed *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                cursor_speed *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * cursor_speed
            y += dy * cursor_speed
            # clamp the tracked position to the map size
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        # else, pass key up to AskUserEH; which will probably cancel back to MainGameEH
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """ Reads left click and confirms a selection """
        if self.engine.game_map.in_bounds(*event.tile) and event.button == 1:
            return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """ Lets the player look around using the keyboard """
    def on_index_selected(self, x: int, y: int) -> None:
        # return to main event handler
        self.engine.event_handler = MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """ Handles targeting a single enemy. """
    def __init__(self,
        engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """ Handles targeting an area within a given radius. Any entity within the area will be affected. """
    def __init__(self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        # highlights the tile under the cursor
        super().on_render(console)

        # draw a rectangle around the targeted area
        x, y = self.engine.mouse_location
        console.draw_frame(
            x - self.radius - 1,
            y - self.radius - 1,
            self.radius ** 2,
            self.radius ** 2,
            fg=colours.RLT.RED,
            clear=False
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
