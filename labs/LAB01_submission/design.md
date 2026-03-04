# Game Design Document

## Theme / Setting
Survival game set in an urban wasteland after a zombie outbreak.

## Player's Goal
Explore various zombie-infested locations
Find the Keycard (randomly spawned in deep locations)
Unlock and reach the Radio Tower
Defeat the Mutated Alpha Boss
Use the Radio to call for helicopter extraction and escape

## Locations (4-6)
1. Safehouse (Start)
2. Downtown (MidGame)
3. Subway Tunnels
4. Overgrown Park
5. Radio Tower

```
                    [Radio Tower]
                    ├─ Ground Floor
                    ├─ Stairwell
                    ├─ Transmitter Room
                    └─ Rooftop Control (BOSS)
                           ↑
                    [Downtown Core]
                    ├─ Main Street (entrance)
                    ├─ Abandoned Mall
                    └─ Dark Alley
        ↙         ↑         ↘
[Safehouse]  [Downtown]  [Subway Tunnels]
(Start)                  ├─ Station Platform
                         ├─ Train Tracks
                         └─ Maintenance Room
                              
                    [Overgrown Park]
                    ├─ Park Entrance
                    ├─ Murky Pond
                    └─ Old Gazebo
```

## Enemies (2-4 types)
Walker (Minion)	HP: 30	STR: 4	DEF: 8	Slow melee zombie, low threat	Infection Chance: 20%

Runner (Elite)	HP: 50	STR: 7	DEF: 11	Fast, aggressive, higher damage	Infection Chance: 25%

Mutated Alpha (Boss)	HP: 120	STR: 12	DEF: 14	Final boss with highest stats, drops Radio	Infection Chance: 35%

## Win Condition
The player wins by:

Acquiring the Keycard (found in subway maintenance or park gazebo)

Traveling north to the Radio Tower (which is locked until keycard is obtained)

Progressing through all 3 interior rooms and defeating the Mutated Alpha Boss

Obtaining the Radio (dropped by boss)

Using the radio at the Rooftop Control to call for extraction
Successfully escaping via helicopter 🎉


## Lose Condition
Health reaches 0 during combat with any enemy

Infection level reaches 100% (succumbs to the virus)

## Class Hierarchy
[Sketch your class design]

```
Character (abstract base class)
├── Player
│   ├── Inventory management
│   ├── Weapon equipping
│   ├── Item usage/consumption
│   └── Critical hit system (20% crit chance)
│
└── Enemy
    ├── Minion (Walker)
    ├── Elite (Runner)
    └── Boss (Mutated Alpha)

Location
├── Entrance locations (is_entrance=True)
├── Interior rooms
├── Locked locations
└── Enemy/item spawning

Combat
├── Turn-based system
├── Player turn actions (attack, use item, run, inventory)
└── Enemy turn actions (attack, infection application)

Game
├── Main game loop
├── State management (exploring, combat, game over, victory)
├── Navigation system
├── Item pickup system
└── Inventory management
```

## Additional Notes
Items scale in quality based on depth:

Entrances: Basic melee weapons + consumables

Mid-rooms: Mid-tier weapons + medkits

Deep rooms: High-tier firearms + best consumables

Boss room: Legendary items (AR-15, Desert Eagle, Radio)

Weapon Arsenal:
Melee: Rusty Bat, Tire Iron, Screwdriver, Pipe, Crowbar
Firearms: Handgun, Mac-10, Revolver, Shotgun, AK-47, AR-15, Desert Eagle

Game Balance Decisions:
Keycard randomization (50/50 spawn in 2 locations) forces replayability

Infection mechanic adds difficulty beyond just HP damage (needs optimization)

Gun availability limited to deep rooms encourages exploration and risk/reward

