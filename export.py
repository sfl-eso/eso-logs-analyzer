from collections import defaultdict
from itertools import chain
from typing import List, Dict

from mdutils import MdUtils
from python_json_config import Config

from formatting import format_time, format_uptime
from models.data import EncounterLog
from models.data.events import UnitAdded
from models.postprocessing import CombatEncounter
from models.postprocessing.effect_uptime import EffectUptime
from trials import Rockgrove
from utils import tqdm


# TODO: class that inherits from Base so we can log stuff here
def generate_markdown_file(config: Config, encounter_log: EncounterLog, combat_encounters: List[CombatEncounter]):
    timestamp = encounter_log.begin_log.time.strftime("%Y_%m_%d_%H_%M_%S")
    # TODO: write to configured directory
    file_name = f"{config.export.dir}/{timestamp}_{config.export.file_suffix}.md"
    # TODO: trial id and header
    md_file: MdUtils = MdUtils(file_name=file_name, title=f"Dragon Aegis - {encounter_log.begin_log.time.strftime('%Y-%m-%d %H:%M:%S')}")
    # TODO: players with metadata

    debuffs = [
        "Crusher",
        "Major Breach",
        "Minor Breach",
        "Crimson Oath's Rive",
        "Minor Vulnerability",
        "Major Vulnerability",
        "Minor Brittle",
        "Flame Weakness",
        "Frost Weakness",
        "Shock Weakness"
    ]

    for encounter in tqdm(combat_encounters, desc="Computing uptimes for encounters"):
        # TODO: handle trash
        if not encounter.is_boss_encounter:
            continue

        # TODO: filter for clears/make bosses configurable
        if encounter.get_boss() != Rockgrove.OAXILTSO:
            continue

        # TODO: is the encounter clear or not
        header_title = f"{encounter.get_boss().value} ({encounter.begin.time.strftime('%H:%M:%S')} - {format_time(encounter.event_span.duration)})"
        md_file.new_header(level=1, title=header_title)

        # TODO: define unit names somewhere (trial profile)?
        __create_encounter_debuff_table(md_file, encounter, ["Oaxiltso", "Havocrel Annihilator"], debuffs)

    # Write the file to disk
    md_file.create_md_file()


def __create_encounter_debuff_table(md_file: MdUtils, encounter: CombatEncounter, units: List[str] = None, debuffs: List[str] = None) -> str:
    """
    Create table for debuff uptimes.
    Each row is an ability.
    Each column is a unit in the encounter.
    The header names are set by the keys of each row's dictionary.
    """
    uptimes: Dict[UnitAdded, List[EffectUptime]] = encounter.debuff_uptimes(debuffs, unit_names=units)

    header_row = ["Name"]
    target_uptimes = ["Uptime of each target"]
    ability_rows: Dict[str, List[str]] = defaultdict(list)

    for unit in uptimes:
        target_uptimes_set = False
        header_row.append(f"{unit.name} ({unit.unit_id})")

        for effect_uptime in uptimes[unit]:
            ability, uptime_in_s, target_time_in_s = effect_uptime.compute_uptime()

            if not target_uptimes_set:
                # TODO: part of a separate unit class
                target_uptimes.append(
                    f"{format_time(effect_uptime.uptime_begin, encounter)} to {format_time(effect_uptime.uptime_end, encounter)} ({format_time(target_time_in_s)})")
                target_uptimes_set = True

            relative_uptime = (uptime_in_s / target_time_in_s)
            ability_rows[ability.name].append(f"{format_uptime(relative_uptime)} ({format_time(uptime_in_s)})")

    table_rows = [header_row, target_uptimes]
    for ability_name, row_data in sorted(ability_rows.items()):
        table_rows.append([ability_name] + row_data)

    md_file.new_line()
    md_file.new_table(columns=len(table_rows[0]), rows=len(table_rows), text=list(chain(*table_rows)), text_align="left")
