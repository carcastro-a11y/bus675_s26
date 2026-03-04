# Zombie Urban Survival

## Story
The world has fallen to a devastating zombie outbreak. Civilization has collapsed, and the undead roam the urban wastelands hunting for survivors. You wake up in a barricaded safehouse—your last shelter. A crackling radio signal hints at a possible extraction point: the Radio Tower on the north edge of the city.

To escape, you must:
- Venture into zombie-infested locations
- Search for supplies and weapons
- Find the mysterious Keycard that unlocks the Radio Tower
- Fight your way to the rooftop and defeat the **Mutated Alpha**—a horrifying boss creature
- Call for helicopter extraction and escape

Time is running out. The infection spreads faster each day. Will you survive?


## How to Play

### Running the Game
```bash
python game.py
```

### Commands
#### Navigation
- `north` / `south` / `east` / `west` - Travel to adjacent locations
- `enter location` - Go inside a location
- `go forward` - Move deeper into a location (only when inside)
- `go backward` - Return to previous room (only when inside)
- `exit location` - Leave and return to the entrance
- `explore` - See what locations are nearby

#### Combat & Inventory
- `fight` / `attack` - Initiate combat with enemies
- `inventory` / `i` - View your items and equipped weapon
- `take [item]` / `grab [item]` / `get [item]` / `pickup [item]` - Pick up items
- `equip [weapon]` - Equip a weapon from inventory
- `use [consumable]` - Consume a medkit, bandage, or food

#### In Combat
- `attack` / `a` - Attack the enemy
- `use [item]` / `u [item]` - Use consumable during combat
- `run` / `r` - Attempt to flee (50% success rate)
- `inventory` / `i` - Check your items mid-combat

#### Other
- `look` - Examine current location details
- `help` - Display command reference
- `quit` - Exit the game


## Goal

**Win Condition:**
1. Explore the world and defeat enemies to gather supplies
2. Find the **Keycard** (hidden in either the Subway Maintenance Room or Park Gazebo)
3. Travel north to the **Radio Tower** (requires Keycard to enter)
4. Progress through 3 interior rooms
5. Defeat the **Mutated Alpha Boss** on the Rooftop
6. Pick up the **Radio** (dropped by boss)
7. Use the radio at Rooftop Control: `use radio`
8. Escape via helicopter extraction 🚁

**Lose Condition:**
- Your health reaches 0 in combat
- Your infection level reaches 100% (infection increases when damaged by enemies)


## Tips
### Exploration Strategy
- 🗺️ **Start at the Safehouse** - Grab the basic melee weapons here before exploring
- 🔍 **Explore all locations before hitting Radio Tower** - You NEED the Keycard first
- 📍 **Deeper = Better Loot** - The further you go into a location, the better weapons you'll find
- ⚔️ **Guns only at the end** - Firearms only appear in the deepest rooms of each location

### Combat Tips
- 💪 **Equip weapons** - Better weapons = more damage. Use `equip [weapon]` before fighting
- 🏥 **Stock up on consumables** - Medkits restore 30 HP, Bandages restore 15 HP
- 🏃 **Know when to retreat** - If you're low on health, try to run away and heal
- 🧠 **Infection is deadly** - Avoid taking unnecessary damage. At 100% infection, you die

