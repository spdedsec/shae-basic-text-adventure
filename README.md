# SHAE BASIC Text Adventure

<div align="center">

```
   ____  _   _    _    _____     ____    _    _     ____
  / ___|| | | |  / \  | ____|   / ___|  / \  | |   / ___|
  \___ \| |_| | / _ \ |  _|    | |     / _ \ | |  | |
   ___) |  _  |/ ___ \| |___   | |___ / ___ \| |__| |___
  |____/|_| |_/_/   \_\_____|   \____/_/   \_\_____\____|
```

**A BASIC-inspired interactive text adventure in pure Python 3.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)
[![CLI](https://img.shields.io/badge/Type-CLI-orange.svg)](#)

</div>

---

## What is this?

**SHAE BASIC Text Adventure** is a terminal-based interactive fiction game written in the spirit of 1980s BASIC adventures. You explore a crumbling castle, collect items, fight enemies, and recover the lost royal crown.

- Multiple connected rooms
- Inventory system
- Combat with enemies
- Win condition (recover the crown)
- Zero external dependencies — pure Python 3 standard library

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [How to Play](#how-to-play)
4. [Commands](#commands)
5. [Features](#features)
6. [Project Structure](#project-structure)
7. [Development](#development)
8. [License](#license)

## Installation

### Prerequisites

- Python 3.9 or newer
- A terminal that supports ANSI escape codes (most modern terminals)

### Install via CLI

```bash
# Clone the repository
git clone https://github.com/spdedsec/shae-basic-text-adventure.git
cd shae-basic-text-adventure

# Run the install script
bash scripts/install.sh
```

The installer creates a wrapper at `~/.local/bin/shae-adventure`. Make sure
`~/.local/bin` is on your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add that line to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to make it
permanent.

### Run directly without installing

```bash
python3 src/main.py
```

## Quick Start

```bash
shae-adventure
```

You will start at the Castle Gate. Follow the on-screen prompts:

```
Type 'help' at any time for a command list. 'quit' to leave.

  Castle Gate
  You stand before the gate of a crumbling castle...
  You see: torch
  Exits: south

 [30hp] > take torch
 [30hp] > go south
```

## How to Play

- **Objective**: Recover the royal crown from the Crown Tower.
- **Combat**: Use `attack <enemy>` to fight. Your damage depends on your
  weapon (bare fists = 3, rusty sword = 8).
- **Health**: Enemies retaliate. Use `healing herb` to recover HP.
- **Exploration**: Some doors are locked; find keys to open them.
- **Win**: Defeat the wraith and take the crown.

## Commands

| Command | Description |
|---------|-------------|
| `look` | Redescribe the current room |
| `go <dir>` | Move north/south/east/west/up/down |
| `take <item>` | Pick up an item |
| `get <item>` | Alias for `take` |
| `drop <item>` | Drop an item |
| `use <item>` | Use an item (heal, unlock, light) |
| `attack <enemy>` | Attack an enemy in the room |
| `inventory` / `i` | List your carried items |
| `status` | Show HP, score, turns, rooms discovered |
| `help` / `?` | Show command list |
| `quit` / `exit` | Leave the game |

## Features

- **Multiple rooms**: castle gate, road, courtyard, chapel, barracks, great
  hall, spiral stair, vault, crown tower.
- **Inventory system**: pick up, drop, and use items.
- **Combat**: turn-based attacks with enemy counterattacks.
- **Win condition**: defeat the wraith and claim the royal crown.
- **Score tracking**: points for items, enemies defeated, and victory.
- **BASIC flavour**: turn counter, RND-style variance, terse output.

## Project Structure

```
shae-basic-text-adventure/
├── src/
│   └── main.py              # Game engine and world definition
├── tests/
│   └── test_game.py         # Pytest test suite
├── scripts/
│   └── install.sh           # CLI install script
├── Makefile                 # Build / test / lint targets
├── pyproject.toml           # Python packaging metadata
├── README.md                # This file
├── DESIGN.md                # Design system notes
└── .github/
    └── workflows/
        └── release.yml      # GitHub release workflow
```

## Development

### Run tests

```bash
make test
# or
python3 -m pytest tests/ -v
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```

## License

MIT License — see [LICENSE](LICENSE).

---

*Built with the SHAE Field Manual design system: warm paper, near-black ink,
oxide signal, flat and physical, motion is typesetting.*