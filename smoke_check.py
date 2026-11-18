#!/usr/bin/env python3
"""Ad-hoc smoke check (no third-party deps). Run: python3 smoke_check.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import main

world = main.build_world()
assert len(world) >= 8, "world too small"
g = main.Game()
assert g.location == "gate"
assert g.player_hp == 30 and g.player_max_hp == 30

g.cmd_go(["south"]); assert g.location == "road"
g.cmd_go(["north"]); assert g.location == "gate"
g.cmd_go(["up"]); assert g.location == "gate"
g.cmd_go(["xyz"]); assert g.location == "gate"

g.cmd_take(["torch"])
assert any(i.name == "torch" for i in g.inventory)
g.cmd_drop(["torch"])
assert any(i.name == "torch" for i in g.world["gate"].items)

g.cmd_use(["healing", "herb"])
g.cmd_status([])
g.cmd_help([])
g.cmd_inventory([])

g.location = "chapel"
en = g.world["chapel"].enemies[0]
orig = en.hp
g.attack("hollow monk")
assert en.hp < orig, "attack did not reduce hp"

g.world["chapel"].enemies[0].hp = 1
before = g.score
g.attack("hollow monk")
assert g.score > before, "score did not increase after kill"

# win condition: crown held, wraith alive -> no win
crown = main.Item(name="royal crown", aliases=["crown"], description="crown")
g.inventory.append(crown)
# wraith alive -> no win expected
try:
    g.check_win()
    # no exception -> no win, as expected
    print("No win when wraith alive - OK")
except main.GameOver:
    print("ERROR: win should not have occurred")
    raise

# kill wraith, hold crown -> win
g.world["tower"].enemies[0].hp = 0
try:
    g.check_win()
    print("ERROR: win should have occurred")
    raise SystemExit("FAIL")
except main.GameOver:
    print("WIN CONDITION OK")

assert main.c("hi") == "hi"
assert "HI" in main.c("HI", "bold", "oxide")
print("SMOKE CHECK PASSED")
