import colours
from entity import Entity


# player
player = Entity("Player", "@", colours.BLUE, blocks_movement=True)

# enemies
orc = Entity("Orc", "o", colours.GREEN, blocks_movement=True)
troll = Entity("Troll", "t", colours.DARK_GREEN, blocks_movement=True)
