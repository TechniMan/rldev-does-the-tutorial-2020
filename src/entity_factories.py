import colours
from components.ai import BaseAI, HostileEnemy
from components.consumable import HealingConsumable
from components.fighter import Fighter
from entity import Actor, Item


# player
player = Actor(
    name="Player",
    char="@",
    colour=colours.BLUE,
    ai_cls=BaseAI,
    fighter=Fighter(30, 2, 5)
)

# items
health_potion = Item(
    char="!",
    colour=colours.HEALTH_RECOVERED,
    name="Health Potion",
    consumable=HealingConsumable(10)
)

# enemies
orc = Actor(
    name="Orc",
    char="o",
    colour=colours.GREEN,
    ai_cls=HostileEnemy,
    fighter=Fighter(10, 0, 3)
)
troll = Actor(
    name="Troll",
    char="t",
    colour=colours.DARK_GREEN,
    ai_cls=HostileEnemy,
    fighter=Fighter(16, 1, 4)
)
