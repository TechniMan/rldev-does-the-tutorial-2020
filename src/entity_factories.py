import colours
from components.ai import BaseAI, HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item


# Maintain each possible type of entity here so we can easily make copies of them
#  for spawning into the game world


# player
player = Actor(
    name="Player",
    char="@",
    colour=colours.PLAYER,
    ai_cls=BaseAI,
    fighter=Fighter(30, 2, 5),
    inventory=Inventory(26)
)

# items
health_potion = Item(
    char="!",
    colour=colours.HEALTH_POTION,
    name="Health Potion",
    consumable=consumable.HealingConsumable(4)
)
lightning_scroll = Item(
    char="~",
    colour=colours.LIGHTNING_SCROLL,
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(20, 5)
)

# enemies
orc = Actor(
    name="Orc",
    char="o",
    colour=colours.ORC,
    ai_cls=HostileEnemy,
    fighter=Fighter(10, 0, 3),
    inventory=Inventory(0)
)
troll = Actor(
    name="Troll",
    char="t",
    colour=colours.TROLL,
    ai_cls=HostileEnemy,
    fighter=Fighter(16, 1, 4),
    inventory=Inventory(0)
)
