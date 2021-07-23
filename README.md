# rldev does the tutorial 2020
## (and also 2021)

![Screenshot of game](/screenshots/2.png?raw=true "Screenshot of game")

Following the tutorial series on https://rogueliketutorials.com weekly alongside all the cool folks on [r/roguelikedev](https://www.reddit.com/r/roguelikedev/wiki/python_tutorial_series).

I will be trying to add my own flair to the code as I go, and especially try to add some of my own features in but I may not get too much time to dedicate to this since I work in programming full time.

*In the 2020 series, I got up to Part 9 and left the project behind. Now the 2021 series has started, I'm using this half-done project as a base to try and finish the series and to finally make my own roguelike!*

## Upcoming features (i.e. soon)
* ~~Maps larger than the screen (wow!) and a camera that follows the player~~
* Turns can take different amounts of time then add the actor to a turn queue according to the gametime they will next act
  * Queue is keyed on gametime (which is based on time units/turns)
  * Average turn takes 20 time units, allowing for 5% precision
  * Full message log shows the gametime the message was triggered on
* ~Slightly improve map generation~
  * ~Tunnels could just go to nearby rooms rather than random, potentially far away rooms~
* Character attributes
  * Strength determines damage in close combat
  * Dexterity determines chance to hit with all weapons
  * Something something dark side
* Experience and levelling up
  * get killz to pay the skill billz
* Really improve map generation
  * Add different flavours for different floors, like a cave generator

## How to run
If you open the project in Visual Studio Code, you can just 'Run' (F5). Or if you prefer, run it with python3 via terminal:

```bash
> py src/main.py
```

## Planned features (ideas for later)
My inspiration for this roguelike is the *Diablo (1997)* computer action role-playing game, so some of these feature ideas are based on my experience playing that.
(note I'm aware these aren't remotely unique within the roguelike space, but Diablo is what I'm using for reference with some tweaks of my own)
* Dungeon floor 0 is a small town with NPCs
  * A town portal scroll takes the player to the surface town, and creates a portal back to where they came from
  * Apothecary sells potions
  * Smith sells and upgrades sharp weapons and heavy armour
  * Innkeeper sells food and drink (maybe drinks could do something interesting...)
  * Tanner sells and upgrades light armour
  * Woodsman sells and upgrades wooden equipment (staves, bows)
  * Librarian sells magic scrolls and magic tomes (i.e. re-usable spells)
    * There is a tome for every scroll, so even a barbarian type character may be interested in Town Portal at least
  * Junker buys the player's junk for scraps
    * Ambitious interesting thought: at levels of scrap invested in the town (e.g. 10, 20, 30 etc pieces of equipment sold) the townsfolks' offerings improve, and/or prices reduce due to extra supply
* Enemies have a chance to drop rubbish equipment that can be sold to townsfolk for scrap
* Every 4 or 5 floors are themed together and the 4th/5th one in the group is a boss floor
* Experience is earned when enemies are defeated; once enough experience is earned, it can be spent to improve attributes
* Character classes:
  * probably nothing more exciting than starter templates e.g. attribute assignment and starting equipment
  * These are some ideas for starting classes:
    * Barbarian starts with 2h weapon and strength
    * Knight starts with armour and constitution
    * Rogue starts with dagger(s?) and dexterity/strength mix
      * I need to consider how dual-wielding will work!
    * Ranger starts with bow and dexterity
      * I need to consider how bows will work re: str/dex attributes
    * Wizard starts with a spell tome and intelligence
    * Sorcerer starts with a few different spell scrolls and intelligence
* Equipment:
  * Weapons have different amounts of damage and time it takes to attack with one
  * Armour - not sure yet if I'll use multiple slots or keep it simple with just a single "Armour" slot

Wow, when it's all written out like that it sure looks like a lot! We'll see how it goes haha D:

![Screenshot of game](/screenshots/1.png?raw=true "Screenshot of game")
