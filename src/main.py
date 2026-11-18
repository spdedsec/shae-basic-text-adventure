#!/usr/bin/env python3
# ========================================================================
# SHAE BASIC Text Adventure
# Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
# License: MIT
#
# A BASIC-inspired interactive text adventure written in pure Python 3
# standard library. Explore rooms, collect items, battle enemies, and
# solve the puzzle to win.
# ========================================================================

from __future__ import annotations

import os
import random
import sys
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Design system constants (SHAE field-manual aesthetic applied to terminal)
# ---------------------------------------------------------------------------
# Colors are ANSI SGR codes chosen to approximate the paper/ink/oxide palette.
# They degrade gracefully on terminals without colour support.

_SUPPORTS_COLOR = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
_COLOUR_SCHEME: Dict[str, str] = {}

if _SUPPORTS_COLOR:
    _COLOUR_SCHEME = {
        "ink": "38;5;16",        # near-black ink
        "paper": "48;5;230",     # warm paper
        "oxide": "38;5;124",     # oxide red signal
        "muted": "38;5;245",     # metadata grey
        "ok": "38;5;22",         # subtle success green
        "err": "38;5;124",       # error oxide
        "bold": "1",
        "reset": "0",
    }


def c(text: str, *styles: str) -> str:
    """Apply ANSI colour codes to *text* for the given style names.

    When colour output is unsupported the text is returned unchanged so the
    game still works in dumb terminals and CI logs.
    """
    if not _SUPPORTS_COLOR or not _COLOUR_SCHEME:
        return text
    codes = ";".join(_COLOUR_SCHEME.get(s, "") for s in styles if s in _COLOUR_SCHEME)
    if not codes:
        return text
    return f"\x1b[{codes}m{text}\x1b[0m"


def hr(char: str = "-", width: int = 72) -> str:
    """Return a horizontal rule of *char* repeated *width* times."""
    return char * width


def panel(title: str, body: str, width: int = 72) -> str:
    """Render a border-defined panel in the spirit of the SHAE design system."""
    top = f"\u250c{hr(chr(0x2500), width - 2)}\u2510"
    bottom = f"\u2514{hr(chr(0x2500), width - 2)}\u2518"
    label = f"\u2502 {c(title, 'bold', 'oxide')} "
    label += " " * (width - 2 - len(title) - 2)
    label += "\u2502"
    body_lines = body.splitlines() or [""]
    rendered = [top, label]
    for line in body_lines:
        rendered.append(f"\u2502 {line:<{width - 4}} \u2502")
    rendered.append(bottom)
    return "\n".join(rendered)


# ---------------------------------------------------------------------------
# Game data model
# ---------------------------------------------------------------------------


class CommandError(Exception):
    """Raised when the player issues an invalid or unparseable command."""


class GameOver(Exception):
    """Raised to terminate the game loop with a final message."""


class ItemKind(Enum):
    """Categories for inventory items."""

    WEAPON = "weapon"
    CONSUMABLE = "consumable"
    KEY = "key"
    TREASURE = "treasure"


@dataclass
class Item:
    """A world object the player can pick up or use."""

    name: str
    aliases: List[str]
    description: str
    kind: ItemKind = ItemKind.TREASURE
    damage: int = 0            # for weapons
    heal: int = 0              # for consumables
    usable: bool = False

    def matches(self, query: str) -> bool:
        return query == self.name or query in self.aliases


@dataclass
class Enemy:
    """A hostile NPC."""

    name: str
    aliases: List[str]
    description: str
    hp: int
    max_hp: int
    damage: int
    defeat_text: str
    drops: List[Item] = field(default_factory=list)

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def matches(self, query: str) -> bool:
        return query == self.name or query in self.aliases


@dataclass
class Room:
    """A location the player can move between."""

    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)   # direction -> room key
    items: List[Item] = field(default_factory=list)
    enemies: List[Enemy] = field(default_factory=list)
    visited: bool = False


# ---------------------------------------------------------------------------
# World definition
# ---------------------------------------------------------------------------


def build_world() -> Dict[str, Room]:
    """Construct the full game world and return a dict keyed by room id."""

    world: Dict[str, Room] = {}

    # ---- ITEM FACTORY --------------------------------------------------
    rusty_sword = Item(
        name="rusty sword",
        aliases=["sword", "blade", "rusted blade"],
        description="A pitted iron sword. Still holds an edge.",
        kind=ItemKind.WEAPON,
        damage=8,
    )
    sword_hit = Item(
        name="sword hit point bonus",
        aliases=["whetstone"],
        description="A coarse whetstone. Rubbing it on a blade sharpens the edge.",
        kind=ItemKind.CONSUMABLE,
    )
    torch = Item(
        name="torch",
        aliases=["light", "lamp"],
        description="A tar-soaked torch that lights the way into dark places.",
        kind=ItemKind.KEY,
        usable=True,
    )
    healing_herb = Item(
        name="healing herb",
        aliases=["herb", "herbs", "plant"],
        description="A fragrant sprig. Chewing it closes wounds.",
        kind=ItemKind.CONSUMABLE,
        heal=15,
        usable=True,
    )
    iron_key = Item(
        name="iron key",
        aliases=["key"],
        description="A heavy iron key with a crown-shaped bow.",
        kind=ItemKind.KEY,
    )
    ruby = Item(
        name="blood ruby",
        aliases=["ruby", "gem", "gemstone"],
        description="A ruby the size of a fist, glowing faintly from within.",
        kind=ItemKind.TREASURE,
    )

    # ---- ROOMS ---------------------------------------------------------
    world["gate"] = Room(
        name="Castle Gate",
        description=(
            "You stand before the gate of a crumbling castle. A heavy portcullis "
            "blocks the northern arch. The wind carries the smell of rust and old "
            "rain. A narrow path leads south back to the road."
        ),
        exits={"south": "road"},
        items=[torch],
    )

    world["road"] = Room(
        name="The King's Road",
        description=(
            "A muddy road stretches between grey fields. Footprints lead north "
            "toward the castle gate. A weathered milestone reads SHAE 2 MI."
        ),
        exits={"north": "gate"},
        items=[healing_herb],
    )

    world["courtyard"] = Room(
        name="Overgrown Courtyard",
        description=(
            "Ivy climbs every wall. A dry fountain stands in the centre. Doors "
            "lead north to the hall, east to the barracks, and west to a chapel. "
            "Something heavy dragged across the flagstones toward the hall."
        ),
        exits={
            "south": "gate",
            "north": "hall",
            "east": "barracks",
            "west": "chapel",
        },
        items=[rusty_sword],
    )

    world["chapel"] = Room(
        name="Ruined Chapel",
        description=(
            "A collapsed altar lies beneath a shattered stained-glass window. "
            "A cloaked figure kneels before it, whispering to something beneath "
            "the floor."
        ),
        exits={"east": "courtyard"},
        items=[healing_herb, sword_hit],
        enemies=[
            Enemy(
                name="hollow monk",
                aliases=["monk", "figure", "cloaked figure"],
                description="A husk in torn robes, eyes burning with a cold flame.",
                hp=18,
                max_hp=18,
                damage=5,
                defeat_text=(
                    "The monk crumples to ash, leaving behind a small iron key."
                ),
                drops=[iron_key],
            )
        ],
    )

    world["barracks"] = Room(
        name="Ruined Barracks",
        description=(
            "Rotted bunks line the walls. A rusted sword rests on a table. The "
            "north wall bears a scratch tally: one survivor still waits."
        ),
        exits={"west": "courtyard"},
        items=[Item(
            name="whetstone",
            aliases=["stone"],
            description="A coarse sharpening stone.",
            kind=ItemKind.CONSUMABLE,
        )],
    )

    world["hall"] = Room(
        name="Great Hall",
        description=(
            "A long table rots under a collapsed chandelier. Two doors face you: "
            "a barred one to the east and a stair to the north."
        ),
        exits={"south": "courtyard", "east": "vault", "north": "stairs"},
    )

    world["stairs"] = Room(
        name="Spiral Stair",
        description=(
            "A spiral stair climbs into darkness. At the top, a heavy oak door "
            "waits. Something below breathes slowly."
        ),
        exits={"south": "hall", "up": "tower"},
    )

    world["vault"] = Room(
        name="Locked Vault",
        description=(
            "An iron-banded door bars your way. A crown-shaped keyhole glints in "
            "the torchlight."
        ),
        exits={"west": "hall"},
    )

    world["tower"] = Room(
        name="Crown Tower",
        description=(
            "Moonlight floods the chamber through a shattered roof. At its centre "
            "sits a great iron throne. The final guardian stirs."
        ),
        exits={"down": "stairs"},
        items=[Item(
            name="royal crown",
            aliases=["crown", "treasure"],
            description="The lost crown of SHAE, heavy with gold and dark magic.",
            kind=ItemKind.TREASURE,
        )],
        enemies=[
            Enemy(
                name="wraith",
                aliases=["ghost", "guardian", "shadow"],
                description="A tall shadow with a crown of frost. Its breath is winter.",
                hp=40,
                max_hp=40,
                damage=9,
                defeat_text=(
                    "The wraith shrieks and dissolves into ash. The crown is free."
                ),
            )
        ],
    )

    return world


# ---------------------------------------------------------------------------
# Game engine
# ---------------------------------------------------------------------------


class Game:
    """The SHAE text adventure engine."""

    HELP_TEXT = (
        "Commands: look, go <dir>, take <item>, use <item>, inventory, "
        "attack <enemy>, status, help, quit."
    )

    DIRECTIONS = {"north": ["north", "n"], "south": ["south", "s"],
                  "east": ["east", "e"], "west": ["west", "w"],
                  "up": ["up", "u"], "down": ["down", "d"]}

    def __init__(self, world: Optional[Dict[str, Room]] = None) -> None:
        self.world = world if world is not None else build_world()
        self.location = "gate"
        self.inventory: List[Item] = []
        self.player_hp = 30
        self.player_max_hp = 30
        self.turns = 0
        self.score = 0
        self.has_visited: Set[str] = set()

    # -- presentation helpers ------------------------------------------
    def _print(self, text: str = "") -> None:
        print(text)

    def _say(self, text: str, style: str = "") -> None:
        self._print(c(text, style) if style else text)

    def _wrap(self, text: str, width: int = 68, indent: str = "") -> str:
        return textwrap.fill(text, width=width,
                              initial_indent=indent, subsequent_indent=indent)

    # -- world description ------------------------------------------------
    def describe_room(self) -> None:
        room = self.world[self.location]
        room.visited = True
        self.has_visited.add(self.location)
        header = f"\u2554{hr(chr(0x2550))}\u2557\n{c(' ' + room.name.upper() + ' ', 'bold', 'ink')}\n"
        self._print()
        self._print(header)
        self._print(self._wrap(room.description))
        self._print()

        # Items on floor
        if room.items:
            names = ", ".join(item.name for item in room.items)
            self._print(c(f"  You see: {names}", "muted"))

        # Enemies present
        for enemy in room.enemies:
            if enemy.alive:
                self._print(c(f"  Enemy here: {enemy.name} (hp {enemy.hp}/{enemy.max_hp})",
                              "err"))

        # Exits
        exits = ", ".join(sorted(room.exits.keys()))
        self._print(c(f"  Exits: {exits}", "muted"))
        self._print()

    # -- inventory ---------------------------------------------------------
    def show_inventory(self) -> None:
        if not self.inventory:
            self._say("Your pack is empty.")
            return
        self._say("Inventory:")
        for item in self.inventory:
            kind = item.kind.value
            detail = []
            if item.kind is ItemKind.WEAPON:
                detail.append(f"+{item.damage} dmg")
            if item.kind is ItemKind.CONSUMABLE and item.heal:
                detail.append(f"heals {item.heal}")
            suffix = f"  ({', '.join(detail)})" if detail else ""
            self._print(f"  - {item.name}{suffix}  [{kind}]")

    def _find_item_in_inventory(self, query: str) -> Optional[Item]:
        for item in self.inventory:
            if item.matches(query):
                return item
        return None

    def _find_item_in_room(self, query: str) -> Optional[Item]:
        room = self.world[self.location]
        for item in room.items:
            if item.matches(query):
                return item
        return None

    def _find_enemy_in_room(self, query: str) -> Optional[Enemy]:
        room = self.world[self.location]
        for enemy in room.enemies:
            if enemy.alive and enemy.matches(query):
                return enemy
        return None

    # -- combat ------------------------------------------------------------
    def _weapon_damage(self) -> int:
        for item in self.inventory:
            if item.kind is ItemKind.WEAPON:
                return item.damage
        return 3  # bare fists

    def attack(self, query: str) -> None:
        enemy = self._find_enemy_in_room(query)
        if enemy is None:
            if any(e.alive for e in self.world[self.location].enemies):
                self._say(f"There is no enemy called '{query}' here.")
            else:
                self._say("There is nothing to attack here.")
            return

        base = self._weapon_damage()
        # Roll slight variance (BASIC games loved RND)
        damage = base + random.randint(0, 2)
        enemy.hp -= damage
        self._print(f"\n{c('>>', 'oxide')} You strike the {enemy.name} for "
                    f"{c(str(damage), 'bold')} damage.")
        if enemy.alive:
            self._print(f"   {enemy.name} hp: {enemy.hp}/{enemy.max_hp}")
            # Enemy counterattacks
            retaliation = enemy.damage + random.randint(0, 1)
            self.player_hp -= retaliation
            self._print(f"   {c(enemy.name, 'err')} hits back for "
                        f"{c(str(retaliation), 'err')} damage.")
            self._print(f"   Your hp: {self.player_hp}/{self.player_max_hp}")
            if self.player_hp <= 0:
                self.player_hp = 0
                raise GameOver(
                    "You have fallen. The castle claims another soul.\n"
                    "GAME OVER."
                )
        else:
            self._print(c("   " + enemy.defeat_text, "ok"))
            self.score += 25
            for drop in enemy.drops:
                self.world[self.location].items.append(drop)

    # -- commands ----------------------------------------------------------
    def cmd_look(self, args: List[str]) -> None:
        self.describe_room()

    def cmd_go(self, args: List[str]) -> None:
        if not args:
            self._say("Go where? Use: go <direction> (north, south, east, west, up, down).")
            return
        direction = args[0].lower()
        # resolve abbreviations
        for full, aliases in self.DIRECTIONS.items():
            if direction == full or direction in aliases:
                direction = full
                break
        else:
            self._say(f"'{direction}' is not a direction I understand.")
            return

        room = self.world[self.location]
        target = room.exits.get(direction)
        if target is None:
            self._say(f"You cannot go {direction}.")
            return
        self.location = target
        self.describe_room()

    def cmd_take(self, args: List[str]) -> None:
        if not args:
            self._say("Take what? Use: take <item>.")
            return
        query = " ".join(args).lower()
        room = self.world[self.location]
        item = self._find_item_in_room(query)
        if item is None:
            self._say(f"You don't see any '{query}' here.")
            return
        # Cannot take items from a room with living enemies blocking?
        room.items.remove(item)
        self.inventory.append(item)
        self._print(f"\n{c('>>', 'oxide')} Taken: {item.name}")
        self.score += 5

    def cmd_drop(self, args: List[str]) -> None:
        if not args:
            self._say("Drop what? Use: drop <item>.")
            return
        query = " ".join(args).lower()
        item = self._find_item_in_inventory(query)
        if item is None:
            self._say(f"You aren't carrying any '{query}'.")
            return
        self.inventory.remove(item)
        self.world[self.location].items.append(item)
        self._print(f"\n{c('>>', 'oxide')} Dropped: {item.name}")

    def cmd_use(self, args: List[str]) -> None:
        if not args:
            self._say("Use what? Use: use <item>.")
            return
        query = " ".join(args).lower()
        item = self._find_item_in_inventory(query)
        if item is None:
            self._say(f"You aren't carrying any '{query}'.")
            return

        # healing consumables
        if item.kind is ItemKind.CONSUMABLE and item.heal:
            if self.player_hp >= self.player_max_hp:
                self._say("You are already at full health.")
                return
            before = self.player_hp
            self.player_hp = min(self.player_max_hp, self.player_hp + item.heal)
            self.inventory.remove(item)
            self._print(f"\n{c('>>', 'oxide')} You use the {item.name}. "
                        f"Recovered {self.player_hp - before} HP.")
            return

        # torch unlocks dark tower room
        if item.name == "torch":
            if self.location == "stairs":
                self._say("The torch reveals the way up to the tower already.")
            else:
                self._say("You raise the torch. It lights the shadows.")
            return

        # iron key opens vault
        if item.name == "iron key":
            if self.location == "vault":
                self._say("The key fits the crown-shaped lock. The vault opens.")
                # simulate unlock: mark door open by removing special description
                # In this prototype we treat the key as usable anywhere.
                return
            else:
                self._say("There is no lock here that fits the iron key.")
                return

        self._say(f"You can't find a use for the {item.name} here.")

    def cmd_attack(self, args: List[str]) -> None:
        if not args:
            # if only one enemy present, attack it
            enemies = [e for e in self.world[self.location].enemies if e.alive]
            if len(enemies) == 1:
                self.attack(enemies[0].name)
                return
            self._say("Attack what? Use: attack <enemy>.")
            return
        query = " ".join(args).lower()
        self.attack(query)

    def cmd_inventory(self, args: List[str]) -> None:
        self.show_inventory()

    def cmd_status(self, args: List[str]) -> None:
        self._print(panel(
            "PLAYER STATUS",
            f"Location : {self.world[self.location].name}\n"
            f"HP       : {self.player_hp}/{self.player_max_hp}\n"
            f"Score    : {self.score}\n"
            f"Turns    : {self.turns}\n"
            f"Rooms    : {len(self.has_visited)}/{len(self.world)} discovered",
        ))

    def cmd_help(self, args: List[str]) -> None:
        self._print(panel("HOW TO PLAY", self.HELP_TEXT))

    def cmd_quit(self, args: List[str]) -> None:
        raise GameOver("You abandon the castle. Farewell, adventurer.")

    # -- win condition -----------------------------------------------------
    def check_win(self) -> None:
        crown_in_inventory = any(
            i.name == "royal crown" for i in self.inventory
        )
        if crown_in_inventory:
            # need wraith dead and crown held
            wraith = self.world["tower"].enemies[0]
            if not wraith.alive:
                self.score += 50
                raise GameOver(
                    "You lift the royal crown of SHAE from the iron throne.\n"
                    "The castle falls silent. Dawn breaks over the ruins.\n\n"
                    f"VICTORY!  Final score: {self.score}"
                )

    # -- main loop ---------------------------------------------------------
    COMMANDS = {
        "look": "cmd_look",
        "go": "cmd_go",
        "take": "cmd_take",
        "get": "cmd_take",
        "drop": "cmd_drop",
        "use": "cmd_use",
        "attack": "cmd_attack",
        "inventory": "cmd_inventory",
        "i": "cmd_inventory",
        "status": "cmd_status",
        "help": "cmd_help",
        "quit": "cmd_quit",
        "exit": "cmd_quit",
        "?": "cmd_help",
    }

    def run(self) -> None:
        """Entry point — runs the interactive game loop."""
        self._print(c("=" * 72, "muted"))
        self._print(c("  S H A E   \u00b7   B A S I C   T E X T   A D V E N T U R E", "bold", "ink"))
        self._print(c("  A field-manual adventure in the spirit of 1980s BASIC.", "muted"))
        self._print(c("=" * 72, "muted"))
        self._print()
        self._say("Type 'help' at any time for a command list. 'quit' to leave.")
        self._print()
        self.describe_room()

        while True:
            self.turns += 1
            try:
                raw = input(c(f" [{self.player_hp}hp] > ", "oxide", "bold")).strip()
            except (EOFError, KeyboardInterrupt):
                self._print()
                raise GameOver("You abandon the castle. Farewell, adventurer.")

            if not raw:
                continue

            parts = raw.split()
            verb = parts[0].lower()
            args = parts[1:]

            handler_name = self.COMMANDS.get(verb)
            if handler_name is None:
                self._say(f"I don't know how to '{verb}'. Type 'help'.")
                continue

            handler = getattr(self, handler_name)
            handler(args)
            self.check_win()


def main() -> None:
    """CLI entry point."""
    game = Game()
    try:
        game.run()
    except GameOver as over:
        self_note = str(over)
        print()
        for line in self_note.splitlines():
            print(c(line, "bold"))
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()