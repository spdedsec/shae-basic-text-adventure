# SHAE BASIC Text Adventure — DESIGN.md

This document describes how the SHAE Field Manual design system is applied to
the BASIC-inspired text adventure CLI.

## Design System Mapping

The SHAE design system is visual-first, but a terminal game must translate the
principles into text and interaction design.

### 1. Precise over decorative

- Output uses monospaced ASCII frames (`┌─┐│└┘`, `═`, `·`) instead of emoji or
  decorative glyphs.
- Metadata (HP, score, turns) is aligned and tabular.
- No ornamental noise: every line of output carries information.

### 2. Confident restraint

- Palette: near-black ink on warm paper ground. In the terminal this maps to
  the default foreground with a small set of ANSI accents.
- Oxide red (`#B3341B` → SGR 124) is reserved for signals: prompts, damage,
  errors, and the `>>` action marker.
- No gradients, glows, shadows, or rounded panels — only hairline rules and
  border-defined boxes.

### 3. Density with air

- Room descriptions wrap to 68 columns, leaving generous margins.
- Blank lines separate sections so the eye can rest.
- The prompt is compact: `[30hp] >`.

### 4. Motion is typesetting, state, and orientation

- A terminal cannot animate, so "motion" is expressed through state changes:
  HP counters, score updates, room transitions, and enemy status lines.
- State is always visible: `status` prints a panel with HP, score, turns, and
  rooms discovered.

### 5. Accessibility is part of the aesthetic

- The game degrades gracefully when colour is unavailable (`TERM=dumb`,
  piped output, CI logs): all ANSI codes are stripped automatically.
- Keyboard-first: every action is a short text command.
- No time pressure: the game waits for input.
- Clear error messages: unknown commands are acknowledged, not ignored.

## Typography

- Terminal monospace font (user-configured).
- Uppercase only for room titles and short labels.
- Tabular alignment for numeric data.

## Colour

| Token   | Terminal SGR | Hex approx | Use |
|---------|--------------|------------|-----|
| ink     | 38;5;16      | #191712    | Body text |
| paper   | 48;5;230     | #F2EEE5    | Background (when supported) |
| oxide   | 38;5;124     | #B3341B    | Prompts, damage, errors, signals |
| muted   | 38;5;245     | #8a8a8a    | Metadata, exits |
| ok      | 38;5;22      | #2d6a2d    | Success messages |

## Anti-patterns avoided

- No emoji, no ASCII art spam, no decorative borders.
- No colour for its own sake; colour is a signal, not decoration.
- No animation loops or screen clearing tricks.
- No centred "hero" screen; the game opens directly into the first room.

## Interaction model

- One command per line.
- Verbs: `look`, `go`, `take`, `get`, `drop`, `use`, `attack`, `inventory`,
  `status`, `help`, `quit`.
- Direction abbreviations: `n`, `s`, `e`, `w`, `u`, `d`.
- Case-insensitive parsing.
- Empty input is ignored.

## Win / lose conditions

- **Win**: defeat the wraith in the Crown Tower and hold the royal crown.
- **Lose**: HP reaches 0.

## Future extensions

- Save/load game state to JSON.
- More rooms, enemies, and puzzles.
- Optional "BASIC mode" that prints lines like `10 PRINT "YOU ARE AT THE GATE"`
  to evoke 1980s listings.