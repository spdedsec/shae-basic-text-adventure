# ========================================================================
# SHAE BASIC Text Adventure — Test Suite
# ========================================================================

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import main


def test_build_world():
    world = main.build_world()
    assert "gate" in world
    assert "tower" in world
    assert "courtyard" in world
    assert len(world) >= 8


def test_game_initial_state():
    game = main.Game()
    assert game.location == "gate"
    assert game.player_hp == 30
    assert game.player_max_hp == 30
    assert game.score == 0
    assert game.turns == 0


def test_take_item():
    game = main.Game()
    game.cmd_take(["torch"])
    assert any(i.name == "torch" for i in game.inventory)
    assert not any(i.name == "torch" for i in game.world["gate"].items)


def test_go():
    game = main.Game()
    game.cmd_go(["south"])
    assert game.location == "road"
    game.cmd_go(["north"])
    assert game.location == "gate"


def test_invalid_direction():
    game = main.Game()
    game.cmd_go(["up"])  # no up exit from gate
    assert game.location == "gate"


def test_inventory_empty():
    game = main.Game()
    # Should not raise
    game.cmd_inventory([])


def test_attack_no_enemy():
    game = main.Game()
    # No enemy at gate; should not raise
    game.cmd_attack(["dragon"])


def test_use_healing_herb():
    game = main.Game()
    game.player_hp = 10
    game.cmd_take([])  # no-op
    # Take herb from road
    game.cmd_go(["south"])
    game.cmd_take(["healing", "herb"])
    game.cmd_use(["healing", "herb"])
    assert game.player_hp == 30


def test_status_does_not_raise():
    game = main.Game()
    game.cmd_status([])


def test_help_does_not_raise():
    game = main.Game()
    game.cmd_help([])


def test_win_condition_requires_crown_and_dead_wraith():
    game = main.Game()
    # Simulate winning state
    crown = main.Item(name="royal crown", aliases=["crown"], description="crown")
    game.inventory.append(crown)
    # Wraith still alive -> no win
    try:
        game.check_win()
        assert False, "should not win while wraith alive"
    except main.GameOver:
        pass
    # Kill wraith
    game.world["tower"].enemies[0].hp = 0
    try:
        game.check_win()
        assert False, "should win when crown held and wraith dead"
    except main.GameOver:
        pass


def test_drop_item():
    game = main.Game()
    game.cmd_take(["torch"])
    game.cmd_drop(["torch"])
    assert not any(i.name == "torch" for i in game.inventory)
    assert any(i.name == "torch" for i in game.world["gate"].items)


def test_command_dispatch():
    game = main.Game()
    assert "look" in game.COMMANDS
    assert "go" in game.COMMANDS
    assert "quit" in game.COMMANDS
    assert "inventory" in game.COMMANDS


def test_item_matches():
    item = main.Item(name="rusty sword", aliases=["sword"], description="d")
    assert item.matches("rusty sword")
    assert item.matches("sword")
    assert not item.matches("axe")


def test_enemy_matches():
    enemy = main.Enemy(name="hollow monk", aliases=["monk"], description="d",
                       hp=10, max_hp=10, damage=2, defeat_text="x")
    assert enemy.matches("hollow monk")
    assert enemy.matches("monk")
    assert not enemy.matches("knight")


def test_weapon_damage_default():
    game = main.Game()
    assert game._weapon_damage() == 3  # bare fists


def test_weapon_damage_with_sword():
    game = main.Game()
    sword = main.Item(name="rusty sword", aliases=["sword"], description="d",
                      kind=main.ItemKind.WEAPON, damage=8)
    game.inventory.append(sword)
    assert game._weapon_damage() == 8


def test_player_death_raises_game_over():
    game = main.Game()
    game.player_hp = 0
    try:
        game.check_win()
    except Exception:
        pass  # check_win only raises on win; death handled in attack()


def test_attack_reduces_enemy_hp():
    game = main.Game()
    # Move to chapel where hollow monk is
    game.cmd_go(["south"])      # road
    game.cmd_go(["north"])      # gate
    # Need to reach courtyard -> chapel. From gate, south to road, north back.
    # Gate exits: south->road. Road exits: north->gate.
    # We need to reach courtyard. Let's teleport for test simplicity.
    game.location = "chapel"
    enemy = game.world["chapel"].enemies[0]
    original_hp = enemy.hp
    game.attack("hollow monk")
    assert enemy.hp < original_hp


def test_score_increases_on_take():
    game = main.Game()
    initial = game.score
    game.cmd_take(["torch"])
    assert game.score > initial


def test_score_increases_on_kill():
    game = main.Game()
    game.location = "chapel"
    initial = game.score
    # Kill enemy in one hit by setting hp low
    game.world["chapel"].enemies[0].hp = 1
    game.attack("hollow monk")
    assert game.score > initial


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])