from pathlib import Path
from typing import List, Dict, Union

import jinja2
from colour import Color
from jinja2 import FileSystemLoader
from python_json_config import Config

from formatting import format_time, format_uptime
from models.data import EncounterLog
from models.postprocessing import CombatEncounter
from trials import Rockgrove
from utils import tqdm

__TEMPLATE_DIR = "templates/"

__NAME_KEY = "Name"


class Cell:
    def __init__(self, value: str, color: Color = None):
        self.value = value
        self.color = color


def render_template(template_name: str, context: dict) -> str:
    environment = jinja2.Environment(loader=FileSystemLoader(__TEMPLATE_DIR))
    # Trim extra whitespace
    environment.trim_blocks = True
    environment.lstrip_blocks = True

    template = environment.get_template(f"{template_name}.jinja2")
    return template.render(context)


def render_to_file(template_name: str, context: dict, output: Union[str, Path]) -> None:
    with open(output, "w") as out_file:
        out_file.write(render_template(template_name, context))


def render_log(encounter_log: EncounterLog, config: Config):
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

    units = ["Oaxiltso", "Havocrel Annihilator"]

    combat_encounters = CombatEncounter.load(encounter_log)
    boss_encounters = [encounter for encounter in combat_encounters if encounter.is_boss_encounter]

    encounters_html = []

    # TODO: group encounters by trial and trial boss (under a separate heading level (h1?))
    for encounter in tqdm(boss_encounters, desc="Computing boss encounter uptimes"):
        # TODO: filter for clears/make bosses configurable
        try:
            # TODO: filter for clears/make bosses configurable
            if encounter.get_boss() != Rockgrove.OAXILTSO:
                continue
        except NotImplementedError:
            continue

        encounter.compute_debuff_uptimes()
        encounters_html.append(render_encounter(encounter, abilities=debuffs, units=units))

    timestamp = encounter_log.begin_log.time.strftime("%Y_%m_%d_%H_%M_%S")
    # TODO: write to configured directory
    # file_name = f"{config.export.dir}/{timestamp}_{config.export.file_suffix}.html"
    file_name = f"output/{timestamp}_{config.export.file_suffix}.html"
    # TODO: add trial name and custom text
    log_title = f"Test Log {timestamp}"
    return render_to_file("log", {"title": log_title, "encounters": encounters_html}, file_name)


def render_encounter(encounter: CombatEncounter, units: List[str] = None, abilities: List[str] = None) -> str:
    is_clear = all([unit.was_killed for unit in encounter.boss_units])
    # TODO: static values and counter
    clear_text = "Kill" if is_clear else "Wipe"

    encounter_title = f"{clear_text} - {encounter.get_boss().value} - {encounter.begin.time.strftime('%H:%M:%S')} - {format_time(encounter.event_span.duration)}"

    # TODO: dps
    # TODO: buff uptimes
    # TODO: mechanic stats
    # TODO: special uptimes

    # Debuff uptimes
    header_row: List[str] = [__NAME_KEY]
    rows: List[Dict[str, Cell]] = []

    units = [unit for unit in encounter.hostile_units if unit.unit.name in units]

    target_active_times = {__NAME_KEY: Cell("Active time of each target")}
    for unit in units:
        header_row.append(unit.display_str)
        active_time_str = f"{format_time(unit.uptime_begin, encounter)} to {format_time(unit.uptime_end, encounter)} ({format_time(unit.duration)})"
        # Use the uptime colors (green=died, red=alive)
        color = format_uptime(unit.was_killed)[1]
        target_active_times[unit.display_str] = Cell(value=active_time_str, color=color)

    for ability_name in abilities:
        row = {__NAME_KEY: Cell(ability_name)}
        for unit in units:
            relative_uptime = unit.relative_uptime_for_ability_name(ability_name)
            total_uptime = unit.uptime_for_ability_name(ability_name)
            percent_str, color = format_uptime(relative_uptime)
            row[unit.display_str] = Cell(value=f"{percent_str} ({format_time(total_uptime)})", color=color)

        rows.append(row)

    debuff_table = render_template("table", {"title": "Debuff uptimes", "header_row": header_row, "active_row": target_active_times, "rows": rows, "open": True})

    return render_template("encounter", {"title": encounter_title, "debuff_table": debuff_table, "open": False})
