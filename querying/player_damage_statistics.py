from models import BeginCombat, UnitAdded


def player_dps_for_encounter(encounter: BeginCombat):
    players = encounter.player_units
    units = encounter.hostile_units

    damage = {unit: {player: None for player in players} for unit in units}

    for player in players:
        for unit in units:
            damage[unit][player] = player.damage_done(encounter, unit)

    return damage


def print_encounter_stats(encounter: BeginCombat, boss_name: str):
    boss = [unit for unit in encounter.boss_units if unit.name == boss_name][0]
    assert boss is not None, f"Encounter has no boss enemy with name {boss_name}"

    duration = encounter.end_combat.time - encounter.time
    damage = player_dps_for_encounter(encounter)
    boss_damage, boss_dps = compute_total_unit_dps(damage, boss)
    total_damage, total_dps = compute_total_dps(damage)

    fight_time_min = int(duration.total_seconds() // 60)
    fight_time_min = ("0" if fight_time_min < 10 else "") + str(fight_time_min)
    fight_time_sec = int(duration.total_seconds() % 60)
    fight_time_sec = ("0" if fight_time_sec < 10 else "") + str(fight_time_sec)

    print(f"Stats for encounter with {boss_name} at {encounter.time.strftime('%Y/%m/%d %H:%M:%S')}")
    print(f"Fight time: {fight_time_min}:{fight_time_sec}")
    print(f"Total {boss_name} dps: {round(boss_dps):,} ({boss_damage:,} damage)")
    print(f"Total dps: {round(total_dps):,} ({total_damage:,} damage)")


def compute_total_unit_dps(damage: dict, unit: UnitAdded):
    total_damage = 0
    total_dps = 0
    for player, player_dps in damage[unit].items():
        total_damage += player_dps["damage_done"]
        total_dps += player_dps["dps"]
    return total_damage, total_dps


def compute_total_dps(damage: dict):
    total_damage = 0
    total_dps = 0
    for unit, unit_dps in damage.items():
        for player, player_dps in unit_dps.items():
            total_damage += player_dps["damage_done"]
            total_dps += player_dps["dps"]
    return total_damage, total_dps
