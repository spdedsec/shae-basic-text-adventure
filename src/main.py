#!/usr/bin/env python3
"""
SHAE Basic Text Adventure
Production-grade text adventure game with SHAE Field Manual design.
"""

import sys
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

@dataclass
class Item:
    name: str
    description: str
    takeable: bool = True
    use_text: str = ""
    damage: int = 0

@dataclass
class Room:
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    locked_exits: Dict[str, str] = field(default_factory=dict)

@dataclass
class Enemy:
    name: str
    description: str
    hp: int
    max_hp: int
    damage: int
    drop: Optional[str] = None

@dataclass
class Player:
    hp: int = 30
    max_hp: int = 30
    inventory: List[str] = field(default_factory=list)
    location: str = "road"
    score: int = 0
    turns: int = 0
    rooms_visited: Set[str] = field(default_factory=set)
    defeated_enemies: Set[str] = field(default_factory=set)

ROOMS = {
    "road": Room(
        name="The King's Road",
        description="A muddy road stretches between grey fields. Footprints lead north toward the castle gate. A weathered milestone reads SHAE 2 MI.",
        exits={"north": "gate"},
        items=["healing herb"]
    ),
    "gate": Room(
        name="Castle Gate",
        description="You stand before the gate of a crumbling castle. A heavy portcullis blocks the northern arch. The wind carries the smell of rust and old rain. A narrow path leads south back to the road.",
        exits={"south": "road"},
        locked_exits={"north": "iron key"},
        items=["torch"],
        enemies=["hollow monk"]
    ),
    "courtyard": Room(
        name="Castle Courtyard",
        description="Weeds crack through flagstones. A dry fountain stands at the center. Doors lead east to the hall and west to the barracks. The gate lies south.",
        exits={"south": "gate", "east": "hall", "west": "barracks"},
        items=["rusty sword"]
    ),
    "hall": Room(
        name="Great Hall",
        description="Tattered banners hang from vaulted beams. A long table bears the remains of a feast. A throne sits atop a dais at the far end. Stairs descend north.",
        exits={"west": "courtyard", "north": "dungeon"},
        enemies=["wraith"]
    ),
    "barracks": Room(
        name="Barracks",
        description="Rows of rotting bunks line the walls. Weapon racks stand empty. A locked chest sits in the corner.",
        exits={"east": "courtyard"},
        locked_exits={"chest": "iron key"},
        items=["iron key"]
    ),
    "dungeon": Room(
        name="Dungeon",
        description="Damp stone walls drip with condensation. Chains hang from the ceiling. A final guardian blocks the way forward.",
        exits={"south": "hall"},
        enemies=["guardian"]
    ),
}

ENEMIES = {
    "hollow monk": Enemy(name="Hollow Monk", description="A robed figure animated by dark purpose. Its face is a void beneath the hood.", hp=18, max_hp=18, damage=5, drop="iron key"),
    "wraith": Enemy(name="Wraith", description="A shifting shadow with burning eyes. It moves without sound.", hp=25, max_hp=25, damage=7, drop=None),
    "guardian": Enemy(name="Guardian", description="A towering construct of stone and ancient magic. Runes glow along its limbs.", hp=40, max_hp=40, damage=10, drop=None),
}

ITEMS = {
    "healing herb": Item("healing herb", "A fragrant sprig that knits flesh.", use_text="You chew the herb. Wounds close.", damage=0),
    "torch": Item("torch", "A resin-soaked brand. Burns bright.", takeable=True, damage=3),
    "rusty sword": Item("rusty sword", "Pitted but serviceable. Better than fists.", damage=8),
    "iron key": Item("iron key", "Heavy iron, wards against rust. Opens the gate and barracks chest.", takeable=True, damage=0),
}

WIDTH = 70

def wrap(text: str) -> str:
    return textwrap.fill(text, width=WIDTH)

def print_box(title: str, lines: List[str]):
    print(f"\n{'=' * WIDTH}")
    print(f" {title} ".center(WIDTH))
    print(f"{'=' * WIDTH}")
    for line in lines:
        print(wrap(line))
    print(f"{'=' * WIDTH}\n")

def print_status(player: Player):
    rooms_found = len(player.rooms_visited)
    total_rooms = len(ROOMS)
    print(f"\n{'=' * WIDTH}")
    print(f" PLAYER STATUS ".center(WIDTH))
    print(f"{'=' * WIDTH}")
    print(f" Location : {player.location:<{WIDTH-13}}")
    print(f" HP       : {player.hp}/{player.max_hp}")
    print(f" Score    : {player.score}")
    print(f" Turns    : {player.turns}")
    print(f" Rooms    : {len(player.rooms_visited)}/{total_rooms} discovered")
    print(f"{'=' * WIDTH}\n")

def show_help():
    print_box("HOW TO PLAY", [
        "Commands: look, go <dir>, take <item>, use <item>, inventory, attack <enemy>, status, help, quit."
    ])

def main():
    player = Player()
    current_room = ROOMS[player.location]
    player.rooms_visited.add(player.location)
    
    print_box("SHAE - BASIC TEXT ADVENTURE", ["A field-manual adventure in the spirit of 1980s BASIC."])
    show_help()
    
    while True:
        current_room = ROOMS[player.location]
        if player.location not in player.rooms_visited:
            player.rooms_visited.add(player.location)
        
        print_box(current_room.name, [current_room.description])
        
        if current_room.items:
            print("You see: " + ", ".join(current_room.items))
        if current_room.enemies:
            for e_name in current_room.enemies:
                enemy = ENEMIES[e_name]
                print(f"A {enemy.name} blocks your path! HP: {enemy.hp}/{enemy.max_hp}")
        
        exits = list(current_room.exits.keys())
        if current_room.locked_exits:
            for direction in current_room.locked_exits:
                if direction not in exits:
                    exits.append(f"{direction} (locked)")
        print("Exits: " + ", ".join(exits))
        
        print(f"\n[{player.hp}hp] > ", end="")
        cmd = input().strip().lower()
        player.turns += 1
        
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=1)
        verb = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        
        if verb in ("quit", "q"):
            print("Farewell, adventurer.")
            break
        elif verb in ("help", "h", "?"):
            show_help()
        elif verb in ("look", "l"):
            continue
        elif verb in ("go", "g", "move"):
            if not arg:
                print("Go where?")
            elif arg in current_room.exits:
                player.location = current_room.exits[arg]
                print(f"You go {arg}.")
            elif arg in current_room.locked_exits:
                required = current_room.locked_exits[arg]
                if required in player.inventory:
                    player.location = current_room.exits[arg]
                    print(f"You unlock the way with the {required} and go {arg}.")
                else:
                    print(f"The way {arg} is locked. You need a {required}.")
            else:
                print("You cannot go that way.")
        elif verb in ("take", "get", "t"):
            if not arg:
                print("Take what?")
            elif arg in current_room.items:
                item = ITEMS[arg]
                if item.takeable:
                    current_room.items.remove(arg)
                    player.inventory.append(arg)
                    print(f"Taken: {arg}")
                else:
                    print("You cannot take that.")
            else:
                print("You don't see that here.")
        elif verb in ("use", "u"):
            if not arg:
                print("Use what?")
            elif arg in player.inventory:
                item = ITEMS[arg]
                if item.use_text:
                    print(item.use_text)
                    if arg == "healing herb":
                        player.hp = min(player.max_hp, player.hp + 10)
                        print(f"HP restored to {player.hp}/{player.max_hp}.")
                        player.inventory.remove(arg)
                    elif arg == "iron key":
                        print("The key fits the lock.")
                else:
                    print(f"You can't use the {arg} that way.")
            else:
                print("You don't have that.")
        elif verb in ("inventory", "i", "inv"):
            if player.inventory:
                print("You carry: " + ", ".join(player.inventory))
            else:
                print("Your pack is empty.")
        elif verb in ("attack", "a", "hit", "fight"):
            if not arg:
                print("Attack what?")
            else:
                enemy_name = None
                for e in current_room.enemies:
                    if arg in e.lower() or arg in ENEMIES[e].name.lower():
                        enemy_name = e
                        break
                if not enemy_name:
                    print("No such enemy here.")
                else:
                    enemy = ENEMIES[enemy_name]
                    weapon = "rusty sword" if "rusty sword" in player.inventory else None
                    dmg = ITEMS[weapon].damage if weapon else 4
                    enemy.hp -= dmg
                    print(f"You strike the {enemy.name} for {dmg} damage.")
                    if enemy.hp <= 0:
                        print(f"The {enemy.name} crumbles to ash", end="")
                        if enemy.drop:
                            print(f", leaving behind a {enemy.drop}.")
                            current_room.items.append(enemy.drop)
                        else:
                            print(".")
                        current_room.enemies.remove(enemy_name)
                        player.defeated_enemies.add(enemy_name)
                        player.score += 50
                        if enemy_name == "guardian":
                            print_box("VICTORY", [
                                "The Guardian falls. The castle is yours.",
                                f"Final Score: {player.score}",
                                f"Turns: {player.turns}",
                                f"Rooms Explored: {len(player.rooms_visited)}/{len(ROOMS)}"
                            ])
                            return
                    else:
                        print(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
                        player.hp -= enemy.damage
                        print(f"The {enemy.name} hits back for {enemy.damage} damage.")
                        if player.hp <= 0:
                            print_box("DEFEATED", [
                                "Your journey ends here.",
                                f"Final Score: {player.score}",
                                f"Turns: {player.turns}"
                            ])
                            return
        elif verb in ("status", "st"):
            print_status(player)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for commands.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFarewell.")
    except EOFError:
        print("\nFarewell.")
