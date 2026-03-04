import random

# ============================================
# DICE FUNCTIONS
# ============================================
def roll_d20():
    """Roll a 20-sided die."""
    return random.randint(1, 20)


def roll_dice(num_dice, sides):
    """Roll multiple dice and return total."""
    return sum(random.randint(1, sides) for _ in range(num_dice))


# ============================================
# CHARACTER BASE CLASS
# ============================================
class Character:
    """Base class for all characters in the game."""

    def __init__(self, name, health, strength, defense):
        self.name = name
        self.max_health = health
        self.health = health
        self.strength = strength
        self.defense = defense
        self.infection_level = 0

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        print(f"{self.name} takes {amount} damage! (HP: {self.health}/{self.max_health})")
        if self.infection_level > 0:
            status = "🦠" if self.infection_level >= 50 else "⚠️"
            print(f"{status} Infection level: {self.infection_level}%")
        if not self.is_alive():
            print(f"{self.name} has fallen!")

    def heal(self, amount):
        old = self.health
        self.health = min(self.max_health, self.health + amount)
        print(f"💚 {self.name} heals {self.health - old} HP! (HP: {self.health}/{self.max_health})")

    def apply_infection(self, amount):
        self.infection_level = min(100, self.infection_level + amount)
        if amount > 0:
            print(f"🦠 {self.name} becomes infected! (Infection: {self.infection_level}%)")
        if self.infection_level >= 100:
            print(f"💀 {self.name} has succumbed to infection!")
            self.health = 0

    def attack(self, target):
        print(f"\n{self.name} attacks {target.name}!")
        attack_roll = roll_d20()
        total_attack = attack_roll + self.strength

        print(f"Roll: {attack_roll} + STR({self.strength}) = {total_attack}")
        print(f"{target.name}'s Defense: {target.defense}")

        if total_attack > target.defense:
            target.take_damage(self.strength)
        else:
            print("Miss!")

    def __str__(self):
        return f"{self.name} (HP: {self.health}/{self.max_health}, STR: {self.strength}, DEF: {self.defense})"


# ============================================
# WEAPON SYSTEM
# ============================================
class Weapon:
    """Weapon data (no ammo system)."""

    def __init__(self, name, min_damage, max_damage, description=""):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.description = description

    def get_damage(self):
        return random.randint(self.min_damage, self.max_damage)

    def __str__(self):
        return f"{self.name} (Damage: {self.min_damage}-{self.max_damage})"


WEAPONS = {
    "Rusty Bat": Weapon("Rusty Bat", 2, 4, "An old baseball bat covered in rust"),
    "Tire Iron": Weapon("Tire Iron", 2, 5, "A heavy metal tire iron"),
    "Screwdriver": Weapon("Screwdriver", 1, 3, "A sharp flathead screwdriver"),
    "Pipe": Weapon("Pipe", 3, 5, "A sturdy metal pipe"),
    "Crowbar": Weapon("Crowbar", 3, 6, "A classic survivor's tool"),
    "Handgun": Weapon("Handgun", 5, 8, "A 9mm handgun"),
    "Mac-10": Weapon("Mac-10", 6, 9, "A compact submachine gun"),
    "Revolver": Weapon("Revolver", 5, 9, "A .357 magnum revolver"),
    "Shotgun": Weapon("Shotgun", 8, 12, "A pump-action shotgun"),
    "AK-47": Weapon("AK-47", 7, 10, "A reliable assault rifle"),
    "AR-15": Weapon("AR-15", 7, 11, "A modern assault rifle"),
    "Desert Eagle": Weapon("Desert Eagle", 6, 10, "A powerful .50 caliber handgun"),
}

CONSUMABLE_ITEMS = {
    "Medkit": {"heal": 30, "description": "Restores 30 HP"},
    "Bandage": {"heal": 15, "description": "Restores 15 HP"},
    "Canned Food": {"heal": 10, "description": "Restores 10 HP"},
}


# ============================================
# PLAYER
# ============================================
class Player(Character):
    def __init__(self, name):
        super().__init__(name, health=100, strength=8, defense=12)
        self.inventory = []
        self.crit_chance = 0.20
        self.equipped_weapon = None

    def pick_up(self, item):
        self.inventory.append(item)
        weapon_indicator = " ⚔️ [WEAPON]" if item in WEAPONS else ""
        consumable_indicator = " 💊 [CONSUMABLE]" if item in CONSUMABLE_ITEMS else ""
        key_indicator = " 🔑 [KEY ITEM]" if item in ["Keycard", "Radio"] else ""
        print(f"\n✅ You picked up: {item}{weapon_indicator}{consumable_indicator}{key_indicator}")

    def show_inventory(self):
        print(f"\n{'='*50}")
        print(f"📦 {self.name}'s Inventory")
        print(f"{'='*50}")
        if self.equipped_weapon:
            print(f"⚔️ Equipped: {self.equipped_weapon}")
        else:
            print(f"⚔️ Equipped: Fists (Damage: {self.strength})")

        if not self.inventory:
            print("Inventory is empty.")
        else:
            print("Items:")
            for item in self.inventory:
                marker = ""
                if item in WEAPONS:
                    marker = " [WEAPON]"
                elif item in CONSUMABLE_ITEMS:
                    marker = " [CONSUMABLE]"
                elif item in ["Keycard", "Radio"]:
                    marker = " [KEY ITEM]"
                print(f"  - {item}{marker}")
        print(f"{'='*50}")

    def equip_weapon(self, weapon_name):
        if weapon_name not in self.inventory:
            print(f"❌ You don't have '{weapon_name}' in your inventory.")
            return False
        if weapon_name not in WEAPONS:
            print(f"❌ '{weapon_name}' is not a weapon.")
            return False
        self.equipped_weapon = WEAPONS[weapon_name]
        print(f"✓ Equipped {self.equipped_weapon}")
        return True

    def use_item(self, item_name):
        if item_name not in self.inventory:
            print(f"❌ You don't have '{item_name}' in your inventory.")
            return False
        if item_name not in CONSUMABLE_ITEMS:
            print(f"❌ '{item_name}' cannot be used.")
            return False

        self.heal(CONSUMABLE_ITEMS[item_name]["heal"])
        self.inventory.remove(item_name)
        print(f"✓ You used {item_name}")
        return True

    def attack(self, target):
        print(f"\n{self.name} attacks {target.name}!")
        attack_roll = roll_d20()
        total_attack = attack_roll + self.strength

        print(f"Roll: {attack_roll} + STR({self.strength}) = {total_attack}")
        print(f"{target.name}'s Defense: {target.defense}")

        is_critical = random.random() < self.crit_chance
        if total_attack > target.defense:
            base_damage = self.strength
            weapon_bonus = self.equipped_weapon.get_damage() if self.equipped_weapon else 0
            if self.equipped_weapon:
                print(f"💥 Weapon bonus: +{weapon_bonus} ({self.equipped_weapon.name})")

            dmg = base_damage + weapon_bonus
            if is_critical:
                dmg *= 2
                print("⚡ CRITICAL HIT!")
            target.take_damage(dmg)
        else:
            print("Miss!")


# ============================================
# ENEMIES
# ============================================
class Enemy(Character):
    def __init__(self, name, health, strength, defense, xp_value=10, loot=None, infection_chance=0.15):
        super().__init__(name, health, strength, defense)
        self.xp_value = xp_value
        self.loot = loot if loot else []
        self.infection_chance = infection_chance


class Minion(Enemy):
    def __init__(self):
        super().__init__("Walker", 30, 4, 8, xp_value=15, loot=[], infection_chance=0.20)


class Elite(Enemy):
    def __init__(self):
        super().__init__("Runner", 50, 7, 11, xp_value=30, loot=[], infection_chance=0.25)


class Boss(Enemy):
    def __init__(self):
        super().__init__("Mutated Alpha", 120, 12, 14, xp_value=100, loot=["Radio"], infection_chance=0.35)


# ============================================
# LOCATION
# ============================================
class Location:
    def __init__(self, name, description, locked=False, is_entrance=False):
        self.name = name
        self.description = description
        self.connections = {}
        self.enemies = []
        self.items = []
        self.locked = locked
        self.is_entrance = is_entrance

    def add_connection(self, direction, location):
        self.connections[direction] = location

    def describe(self):
        print(f"\n{'='*50}")
        print(f"📍 {self.name}")
        print(f"{'='*50}")
        print(self.description)

        if self.enemies:
            print("\n⚠️ ENEMIES HERE:")
            for e in self.enemies:
                print(f"  - {e.name} (HP: {e.health}/{e.max_health})")
        else:
            print("\n✅ This area is clear of enemies.")

        if self.items:
            print("\n💰 ITEMS YOU CAN PICK UP:")
            for item in self.items:
                w = " [WEAPON]" if item in WEAPONS else ""
                c = " [CONSUMABLE]" if item in CONSUMABLE_ITEMS else ""
                k = " [KEY ITEM]" if item in ["Keycard", "Radio"] else ""
                print(f"  - {item}{w}{c}{k}")

        print(f"{'='*50}")


# ============================================
# WORLD
# ============================================
def create_world():
    # Safehouse (entrance only)
    safehouse = Location(
        "Suburban Safehouse",
        "A barricaded home serving as your base.",
        is_entrance=True
    )
    safehouse.items.extend(["Rusty Bat", "Tire Iron", "Bandage"])

    # Downtown (entrance + 2 rooms)
    downtown_entrance = Location(
        "Downtown Core - Main Street",
        "Overturned cars and broken storefronts. A decent place to start.",
        is_entrance=True
    )
    downtown_mall = Location(
        "Downtown Core - Abandoned Mall",
        "A dark mall full of overturned displays and eerie silence."
    )
    downtown_alley = Location(
        "Downtown Core - Dark Alley",
        "A narrow alley with moving shadows and the stench of decay."
    )

    downtown_mall.enemies.append(Minion())
    downtown_alley.enemies.append(Minion())

    # Downtown loot - NO guns in entrance/mall, guns only in deepest room
    downtown_entrance.items.extend(["Pipe", "Crowbar", "Bandage"])
    downtown_mall.items.extend(["Canned Food", "Medkit"])
    downtown_alley.items.extend(["Revolver", "Shotgun", "Bandage", "Medkit"])  # Guns here

    downtown_entrance.add_connection("forward", downtown_mall)
    downtown_mall.add_connection("exit", downtown_entrance)
    downtown_mall.add_connection("forward", downtown_alley)
    downtown_alley.add_connection("exit", downtown_mall)

    # Subway (entrance + 2 rooms)
    subway_entrance = Location(
        "Subway Tunnels - Station Platform",
        "Emergency lights flicker in the dark. A musty smell fills the air.",
        is_entrance=True
    )
    subway_tracks = Location(
        "Subway Tunnels - Train Tracks",
        "Abandoned tracks fade into darkness. Something rustles in the shadows."
    )
    subway_maintenance = Location(
        "Subway Tunnels - Maintenance Room",
        "Tools and rusted pipes line the walls. A stronghold of supplies."
    )

    subway_tracks.enemies.append(Elite())
    subway_maintenance.enemies.append(Minion())

    # Subway loot - NO guns in entrance/tracks, guns only in deepest room
    subway_entrance.items.extend(["Flashlight", "Bandage", "Canned Food"])
    subway_tracks.items.extend(["Canned Food", "Medkit"])
    subway_maintenance.items.extend(["Mac-10", "AK-47", "Medkit", "Bandage"])  # Guns here

    subway_entrance.add_connection("forward", subway_tracks)
    subway_tracks.add_connection("exit", subway_entrance)
    subway_tracks.add_connection("forward", subway_maintenance)
    subway_maintenance.add_connection("exit", subway_tracks)

    # Park (entrance + 2 rooms)
    park_entrance = Location(
        "Overgrown Park - Park Entrance",
        "Vines and weeds cover old pathways. Nature has reclaimed this place.",
        is_entrance=True
    )
    park_pond = Location(
        "Overgrown Park - Murky Pond",
        "A stagnant pond covered in algae. Dead fish float in the water."
    )
    park_gazebo = Location(
        "Overgrown Park - Old Gazebo",
        "A rotting gazebo creaks in the wind. Hidden treasures may lie here."
    )

    park_pond.enemies.append(Minion())
    park_gazebo.enemies.append(Elite())

    # Park loot - NO guns in entrance/pond, guns only in deepest room
    park_entrance.items.extend(["Screwdriver", "Bandage", "Canned Food"])
    park_pond.items.extend(["Pipe", "Tire Iron", "Canned Food"])
    park_gazebo.items.extend(["AR-15", "Desert Eagle", "Medkit", "Bandage"])  # Guns here

    park_entrance.add_connection("forward", park_pond)
    park_pond.add_connection("exit", park_entrance)
    park_pond.add_connection("forward", park_gazebo)
    park_gazebo.add_connection("exit", park_pond)

    # Radio tower (entrance + 2 rooms + boss room)
    radio_entrance = Location(
        "Radio Tower - Ground Floor",
        "The base of a towering communications structure. Equipment lies scattered about.",
        locked=True,
        is_entrance=True
    )
    radio_stairs = Location(
        "Radio Tower - Stairwell",
        "A spiraling staircase ascends into darkness. Distant mechanical sounds echo."
    )
    radio_transmitter = Location(
        "Radio Tower - Transmitter Room",
        "Advanced broadcasting equipment covers the walls. Almost there..."
    )
    radio_roof = Location(
        "Radio Tower - Rooftop Control",
        "The final chamber. A massive boss emerges from the shadows!"
    )

    radio_stairs.enemies.append(Minion())
    radio_transmitter.enemies.append(Elite())
    radio_roof.enemies.append(Boss())

    # Radio tower loot - NO guns in entrance/stairs, better guns before boss, best after
    radio_entrance.items.extend(["Handgun", "Bandage", "Canned Food"])
    radio_stairs.items.extend(["Medkit", "Bandage", "Canned Food"])
    radio_transmitter.items.extend(["Shotgun", "AK-47", "Medkit"])  # Better guns before boss
    radio_roof.items.extend(["AR-15", "Desert Eagle", "Medkit"])  # Best loot after boss

    radio_entrance.add_connection("forward", radio_stairs)
    radio_stairs.add_connection("exit", radio_entrance)
    radio_stairs.add_connection("forward", radio_transmitter)
    radio_transmitter.add_connection("exit", radio_stairs)
    radio_transmitter.add_connection("forward", radio_roof)
    radio_roof.add_connection("exit", radio_transmitter)

    # Cardinal travel between major entrances
    safehouse.add_connection("north", downtown_entrance)
    downtown_entrance.add_connection("south", safehouse)
    downtown_entrance.add_connection("east", subway_entrance)
    subway_entrance.add_connection("west", downtown_entrance)
    downtown_entrance.add_connection("west", park_entrance)
    park_entrance.add_connection("east", downtown_entrance)
    downtown_entrance.add_connection("north", radio_entrance)
    radio_entrance.add_connection("south", downtown_entrance)

    # 50/50 keycard spawn in deep locations
    if random.random() < 0.5:
        subway_maintenance.items.append("Keycard")
    else:
        park_gazebo.items.append("Keycard")

    return safehouse


# ============================================
# COMBAT
# ============================================
class Combat:
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    COMBAT_END = "combat_end"

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = Combat.PLAYER_TURN

    def start(self):
        print(f"\n⚔️ COMBAT: {self.player.name} vs {self.enemy.name}")
        while self.state != Combat.COMBAT_END:
            if self.state == Combat.PLAYER_TURN:
                self.player_turn()
            else:
                self.enemy_turn()
        return self.get_result()

    def player_turn(self):
        print(f"\n{self.player} | {self.enemy}")
        print("Actions: (a)ttack, (u)se [item], (r)un, (i)nventory")
        action = input("> ").strip().lower()
        parts = action.split()
        if not parts:
            return
        cmd = parts[0]

        if cmd in ["a", "attack"]:
            self.player.attack(self.enemy)
            self.state = Combat.COMBAT_END if not self.enemy.is_alive() else Combat.ENEMY_TURN

        elif cmd in ["u", "use"]:
            if len(parts) < 2:
                print("Use what?")
                return
            raw = " ".join(parts[1:])
            matched = next((i for i in self.player.inventory if i.lower() == raw.lower()), None)
            if matched and self.player.use_item(matched):
                self.state = Combat.ENEMY_TURN

        elif cmd in ["r", "run"]:
            if random.random() < 0.5:
                print("✅ You fled combat.")
                self.state = Combat.COMBAT_END
            else:
                print("❌ Escape failed.")
                self.state = Combat.ENEMY_TURN

        elif cmd in ["i", "inventory"]:
            self.player.show_inventory()

    def enemy_turn(self):
        print(f"\n{self.enemy.name} attacks!")
        attack_roll = roll_d20() + self.enemy.strength
        if attack_roll > self.player.defense:
            damage = roll_dice(1, 4) + self.enemy.strength
            self.player.take_damage(damage)
            if random.random() < self.enemy.infection_chance:
                self.player.apply_infection(roll_dice(1, 3) + 5)
        else:
            print(f"{self.enemy.name} misses.")
        self.state = Combat.COMBAT_END if not self.player.is_alive() else Combat.PLAYER_TURN

    def get_result(self):
        if not self.enemy.is_alive():
            return "victory"
        if not self.player.is_alive():
            return "defeat"
        return "fled"


# ============================================
# GAME
# ============================================
class Game:
    EXPLORING = "exploring"
    IN_COMBAT = "in_combat"
    GAME_OVER = "game_over"
    VICTORY = "victory"

    def __init__(self):
        self.player = None
        self.current_location = None
        self.state = Game.EXPLORING
        self.game_running = True
        self.in_location = False
        self.active_location_entrance = None

    def start(self):
        self.show_intro()
        self.create_player()
        self.current_location = create_world()
        
        # Start OUTSIDE the safehouse so cardinal travel works
        self.in_location = False
        self.active_location_entrance = None
        
        self.current_location.describe()

        while self.game_running:
            if self.state == Game.EXPLORING:
                self.exploration_loop()
            elif self.state == Game.GAME_OVER:
                self.show_game_over()
                break
            elif self.state == Game.VICTORY:
                self.show_victory()
                break

    def show_intro(self):
        print("\n" + "=" * 60)
        print("🧟 ZOMBIE SURVIVAL: TEXT ADVENTURE 🧟")
        print("=" * 60)
        print("Use NORTH/SOUTH/EAST/WEST to travel to locations.")
        print("Type ENTER to go inside a location.")
        print("Inside location: GO FORWARD / GO BACKWARD / EXIT LOCATION")
        print("💡 Explore deeper for better loot and the Keycard!")
        print("=" * 60)

    def create_player(self):
        print("\nWhat is your name, survivor?")
        name = input("> ").strip() or "Survivor"
        self.player = Player(name)
        print(f"Welcome, {name}!")

    # ---------- Main loop ----------
    def exploration_loop(self):
        self.show_actions()
        command = input("> ").lower().strip()
        if not command:
            return

        # explicit multi-word commands
        if command == "go forward":
            self.move_forward()
            return
        if command == "go backward":
            self.move_backward()
            return
        if command == "exit location":
            self.exit_location()
            return

        parts = command.split()
        action = parts[0]

        if action == "help":
            self.show_help()
        elif action == "look":
            self.current_location.describe()

        elif action in ["north", "south", "east", "west"]:
            self.travel_direction(action)
        elif action == "enter":
            self.enter_location()
        elif action == "forward":
            self.move_forward()
        elif action in ["backward", "back", "return", "exit"]:
            self.move_backward()
        elif action == "explore":
            self.show_adjacent_locations()

        elif action in ["inventory", "i"]:
            self.player.show_inventory()
        elif action in ["fight", "attack"]:
            self.initiate_combat()

        elif action in ["take", "grab", "get", "pickup"]:
            item_name = " ".join(parts[1:]) if len(parts) > 1 else None
            self.pick_up_item(item_name)
        elif action == "pick" and len(parts) > 1 and parts[1] == "up":
            item_name = " ".join(parts[2:]) if len(parts) > 2 else None
            self.pick_up_item(item_name)

        elif action in ["equip", "wield"]:
            weapon_name = " ".join(parts[1:]) if len(parts) > 1 else None
            self.equip_weapon(weapon_name)

        elif action == "use":
            if "radio" in self.current_location.name.lower() and "rooftop" in self.current_location.name.lower() and len(parts) > 1 and parts[1] == "radio":
                self.use_radio()
            else:
                item_name = " ".join(parts[1:]) if len(parts) > 1 else None
                if not item_name:
                    print("Use what?")
                    return
                matched = next((i for i in self.player.inventory if i.lower() == item_name.lower()), None)
                if not matched:
                    print(f"❌ You don't have '{item_name}'.")
                    return
                self.player.use_item(matched)

        elif action == "quit":
            print("Thanks for playing!")
            self.game_running = False
        else:
            print("I don't understand that command. Type 'help'.")

    def show_actions(self):
        print("\n" + "=" * 60)
        print("⚡ WHAT DO YOU DO?")
        print("=" * 60)

        print("\n🗺️ EXPLORE:")
        if self.in_location:
            # INSIDE a location: only forward/backward/exit
            if "forward" in self.current_location.connections:
                dest = self.current_location.connections["forward"]
                warning = "⚠️ ENEMIES" if dest.enemies else "✅ CLEAR"
                print(f"   go forward - {dest.name} ({warning})")
            if "exit" in self.current_location.connections:
                back_dest = self.current_location.connections["exit"]
                print(f"   go backward - {back_dest.name}")
            print("   exit location - leave this location")
        else:
            # AT THE ENTRANCE: show enter + cardinal directions
            print("   enter location - go inside")
            for d, dest in self.current_location.connections.items():
                if d in ["north", "south", "east", "west"]:
                    lock = " 🔒" if dest.locked else ""
                    print(f"   {d} - travel to {dest.name}{lock}")

        # Show items when inside locations only
        if self.in_location and self.current_location.items:
            print("\n📦 PICK UP ITEMS:")
            for item in self.current_location.items[:5]:
                print(f"   take {item.lower()}")

        if self.current_location.enemies:
            print("\n⚠️ ENEMIES HERE:")
            for e in self.current_location.enemies:
                print(f"   {e.name} (HP: {e.health}/{e.max_health})")
            print("   type 'fight'")

        print("\n🎒 INVENTORY:")
        print("   inventory (i)")
        if any(i in WEAPONS for i in self.player.inventory):
            print("   equip [weapon]")
        if any(i in CONSUMABLE_ITEMS for i in self.player.inventory):
            print("   use [consumable]")

        print("=" * 60)
        print("Type 'quit' to exit the game")

    # ---------- Navigation ----------
    def show_adjacent_locations(self):
        if self.in_location:
            print("❌ Exit the location first.")
            return
        dirs = [d for d in self.current_location.connections if d in ["north", "south", "east", "west"]]
        if not dirs:
            print("No adjacent locations from here.")
            return

        print("\n🧭 Adjacent locations:")
        for d in dirs:
            print(f"  - {d}: {self.current_location.connections[d].name}")

    def travel_direction(self, direction):
        """Travel to adjacent location. Player arrives at entrance (front steps)."""
        if self.in_location:
            print("❌ You are inside a location. Type 'exit location' first.")
            return
        if direction not in self.current_location.connections:
            print(f"❌ You can't go {direction} from here.")
            return

        destination = self.current_location.connections[direction]
        if destination.locked and "Keycard" not in self.player.inventory:
            print("🔒 That location is locked. You need the Keycard.")
            return

        self.current_location = destination
        print(f"\n🚶 You travel {direction}...")
        self.current_location.describe()

    def enter_location(self):
        """Enter the current location (must be at entrance/front steps)."""
        if self.in_location:
            print("❌ You are already inside a location.")
            return

        if not self.current_location.is_entrance:
            print("❌ You must be at an entrance to enter a location.")
            return

        self.in_location = True
        self.active_location_entrance = self.current_location

        print(f"\n🚶 You enter {self.current_location.name}...")
        
        if self.current_location.enemies:
            self.trigger_ambush()

    def move_forward(self):
        """Move deeper into current location (only works when inside)."""
        if not self.in_location:
            print("❌ You are not inside a location. Type 'enter location' first.")
            return
        if "forward" not in self.current_location.connections:
            print("❌ You can't move forward from here.")
            return

        self.current_location = self.current_location.connections["forward"]
        print("\n🚶 You move forward...")
        self.current_location.describe()

        if self.current_location.enemies:
            self.trigger_ambush()

    def move_backward(self):
        """Go backward one room (only works when inside)."""
        if not self.in_location:
            print("❌ You are not inside a location.")
            return
        if "exit" not in self.current_location.connections:
            print("❌ You can't go backward from here.")
            return

        self.current_location = self.current_location.connections["exit"]
        print("\n🚶 You move backward...")
        self.current_location.describe()

    def exit_location(self):
        """Leave the location and return to its entrance (front steps)."""
        if not self.in_location:
            print("❌ You are not inside a location.")
            return

        # Walk back to entrance through exit links
        while self.current_location != self.active_location_entrance:
            if "exit" not in self.current_location.connections:
                break
            self.current_location = self.current_location.connections["exit"]

        self.in_location = False
        self.active_location_entrance = None

        print("\n↩️ You exit the location and return to the front.")
        self.current_location.describe()

    def trigger_ambush(self):
        """Automatically trigger combat with scary flavor text."""
        enemy = self.current_location.enemies[0]
        
        # Scary ambush messages based on enemy type
        if enemy.name == "Walker":
            messages = [
                f"💀 A {enemy.name} lurches out from the shadows!",
                f"💀 You hear a groan... a {enemy.name} stumbles toward you!",
                f"💀 A {enemy.name} emerges from the darkness, arms outstretched!",
                f"💀 Behind you! A {enemy.name} has spotted you!",
            ]
        elif enemy.name == "Runner":
            messages = [
                f"⚠️ A {enemy.name} drops from the ceiling!",
                f"⚠️ You hear rapid footsteps... a {enemy.name} charges at you!",
                f"⚠️ A {enemy.name} sprints from around the corner!",
                f"⚠️ Something fast moves in the shadows... a {enemy.name} attacks!",
            ]
        else:  # Boss
            messages = [
                f"🔥 The massive {enemy.name} roars and charges!",
                f"🔥 A monstrous {enemy.name} blocks your path!",
                f"🔥 The ground shakes... the {enemy.name} has found you!",
            ]
        
        print(f"\n{random.choice(messages)}")
        self.auto_combat()

    # ---------- Combat / items ----------
    def initiate_combat(self):
        if not self.current_location.enemies:
            print("❌ No enemies here.")
            return
        self.auto_combat()

    def auto_combat(self):
        while self.current_location.enemies and self.player.is_alive():
            enemy = self.current_location.enemies[0]
            result = Combat(self.player, enemy).start()

            if result == "victory":
                self.current_location.enemies.remove(enemy)
                print(f"✅ Defeated {enemy.name}!")
                for loot in enemy.loot:
                    print(f"💎 {enemy.name} dropped {loot}")
                    self.player.pick_up(loot)
            elif result == "defeat":
                self.state = Game.GAME_OVER
                return
            else:  # fled
                print("🏃 You fled combat.")
                return

    def pick_up_item(self, item_name=None):
        if self.current_location.enemies:
            print("❌ Defeat enemies first.")
            return
        if not self.current_location.items:
            print("❌ No items here.")
            return
        if not item_name:
            print("Items here:")
            for i in self.current_location.items:
                print(f" - {i}")
            return

        matched = next((i for i in self.current_location.items if i.lower() == item_name.lower()), None)
        if not matched:
            print(f"❌ No '{item_name}' here.")
            return

        self.current_location.items.remove(matched)
        self.player.pick_up(matched)

    def equip_weapon(self, weapon_name=None):
        if not weapon_name:
            weapons = [i for i in self.player.inventory if i in WEAPONS]
            if not weapons:
                print("No weapons in inventory.")
                return
            print("Weapons:")
            for w in weapons:
                print(f" - {w}")
            return

        matched = next((i for i in self.player.inventory if i.lower() == weapon_name.lower()), None)
        if not matched:
            print(f"❌ You don't have '{weapon_name}'.")
            return
        self.player.equip_weapon(matched)

    def use_radio(self):
        if "rooftop control" not in self.current_location.name.lower():
            print("❌ You can only use radio at the Rooftop Control.")
            return
        if "Radio" not in self.player.inventory:
            print("❌ You don't have a Radio.")
            return
        if self.current_location.enemies:
            print("❌ Clear enemies first.")
            return

        print("📡 You call for extraction...")
        print("🚁 Helicopter inbound.")
        self.state = Game.VICTORY

    # ---------- UI ----------
    def show_help(self):
        print("\n" + "=" * 70)
        print("📜 COMMANDS")
        print("=" * 70)
        print("north/south/east/west - travel to adjacent location")
        print("enter location        - go inside current location")
        print("go forward            - go deeper in current location")
        print("go backward           - go to previous room in location")
        print("exit location         - leave location and return to entrance")
        print("take/get/grab/pickup [item]")
        print("equip [weapon]")
        print("use [consumable]")
        print("fight")
        print("look")
        print("inventory (i)")
        print("quit")
        print("=" * 70)

    def show_game_over(self):
        print("\n💀 GAME OVER")
        print(f"You fell at: {self.current_location.name}")

    def show_victory(self):
        print("\n🎉 VICTORY! You escaped!")
        print(f"Final HP: {self.player.health}/{self.player.max_health}")


if __name__ == "__main__":
    Game().start()