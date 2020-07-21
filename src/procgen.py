from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING
import tcod

import entity_factories
from game_map import GameMap
import tile_types


if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + height

    @property
    def centre(self) -> Tuple[int, int]:
        centre_x = int((self.x1 + self.x2) / 2)
        centre_y = int((self.y1 + self.y2) / 2)
        return (centre_x, centre_y)

    @property
    def inner(self) -> Tuple[slice, slice]:
        """ Return the inner area of this room as a 2D array index """
        return (slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2))

    def intersects(self, other: RectangularRoom) -> bool:
        """ Returns True if this and `other` overlap """
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """ Return an L-shaped tunnel between the two given points """
    x1, y1 = start
    x2, y2 = end
    # 50% chance to go horizontal then vertical
    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    # otherwise, go vertical then horizontal
    else:
        corner_x, corner_y = x1, y2

    # yield for each co-ordinate of the tunnel (to iterate)
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def choose_random_point_in_room(
    room: RectangularRoom
) -> Tuple[int, int]:
    return (random.randint(room.x1 + 1, room.x2 - 1), random.randint(room.y1 + 1, room.y2 - 1))


def place_entities(
    room: RectangularRoom,
    dungeon: GameMap,
    enemies_per_room: Tuple[int, int],
    items_per_room: Tuple[int, int]
) -> None:
    # choose a random number of enemies to place in the room
    number_of_enemies = random.randint(enemies_per_room[0], enemies_per_room[1])
    number_of_items = random.randint(items_per_room[0], items_per_room[1])

    for i in range(number_of_enemies):
        # find a random spot to place them in
        x, y = choose_random_point_in_room(room)

        # if there isn't another entity there:
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            # randomly choose what type of enemy to add. 80% orc, 20% troll
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x, y = choose_random_point_in_room(room)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()
            if item_chance < 0.7:
                entity_factories.health_potion.spawn(dungeon, x, y)
            else:
                entity_factories.lightning_scroll.spawn(dungeon, x, y)


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    enemies_per_room: Tuple[int, int],
    items_per_room: Tuple[int, int],
    engine: Engine
) -> GameMap:
    """ Generate a new dungeon map """
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])
    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)
        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(1, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)
        # if this room intersects with any other room, then discard it and try again
        # although this could make an interesting dungeon; I'll investigate in future
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        # 'carve' out the inner area of this room
        dungeon.tiles[new_room.inner] = tile_types.floor

        # if this is the first room, then put the player in it
        if len(rooms) == 0:
            player.place(*new_room.centre, dungeon)
        # otherwise:
        else:
            # carve a tunnel to the previous room
            for x, y in tunnel_between(rooms[-1].centre, new_room.centre):
                dungeon.tiles[x, y] = tile_types.floor
            # try to add some enemies to this room
            place_entities(new_room, dungeon, enemies_per_room, items_per_room)

        # save this room to the list ready for the next room
        rooms.append(new_room)
    # end for r in range(max_rooms)

    return dungeon
