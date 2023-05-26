import uuid
from pathlib import Path
from typing import List, Dict, Union

import jinja2
from colour import Color
from jinja2 import FileSystemLoader
from python_json_config import Config

from ..formatting import format_time, format_uptime
from ..models.data import EncounterLog
from ..models.postprocessing import CombatEncounter
from ..trials import Rockgrove
from ..utils import tqdm

__TEMPLATE_DIR = "templates/"
__NAME_KEY = "Name"


class Cell:
    def __init__(self, value: str, color: Color = None):
        self.value = value
        self.color = color


def __render_table(**kwargs) -> str:
    context = dict(kwargs)
    # Unique for each table to enable collapsing with boostrap
    context["table_id"] = str(uuid.uuid4())
    return render_template("table", context)


def __render_encounter(**kwargs) -> str:
    context = dict(kwargs)
    # Unique for each encounter to enable collapsing with boostrap
    context["encounter_id"] = str(uuid.uuid4())
    return render_template("encounter", context)


def render_template(template_name: str, context: dict) -> str:
    environment = jinja2.Environment(loader=FileSystemLoader(__TEMPLATE_DIR))
    # Trim extra whitespace
    environment.trim_blocks = True
    environment.lstrip_blocks = True

    template = environment.get_template(f"{template_name}.jinja2")
    return template.render(context)


def render_to_file(template_name: str, context: dict, output: Union[str, Path]) -> None:
    print(f"Rendering template {template_name} to {output}")
    with open(output, "w") as out_file:
        out_file.write(render_template(template_name, context))


def render_readme(config: Config):
    pages = []

    out_path = Path(config.export.path)
    for file in out_path.iterdir():
        if not file.is_file() or file.suffix != ".html" or file.name == "index.html":
            continue

        # TODO: read html and get title element
        name = file.stem
        pages.append((file.stem, name))

    file_name = f"{config.export.path}/index.html"
    return render_to_file("readme", {
        "title": config.export.title_prefix,
        "pages": pages,
        "url_prefix": config.web.url_prefix
    }, file_name)


def render_log(encounter_log: Union[EncounterLog, List[EncounterLog]], config: Config):
    debuffs = sorted([
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
    ])

    hostile_units = ["Oaxiltso", "Havocrel Annihilator"]

    combat_encounters = []
    if isinstance(encounter_log, list):
        for log in encounter_log:
            combat_encounters.extend(CombatEncounter.load(log))
        encounter_log = encounter_log[0]
    else:
        combat_encounters = CombatEncounter.load(encounter_log)

    boss_encounters = [encounter for encounter in combat_encounters if encounter.is_boss_encounter]
    # Sort first by encounter time and then by boss
    # TODO: sort by boss order in trial and not by name
    boss_encounters = sorted(boss_encounters, key=lambda encounter: (encounter.begin, encounter.get_boss))

    encounters_html = []

    log_trial_name = ""

    # TODO: group encounters by trial and trial boss (under a separate heading level (h1?))
    for encounter in tqdm(boss_encounters, desc="Computing boss encounter uptimes"):
        # TODO: filter for clears/make bosses configurable
        try:
            # TODO: filter for clears/make bosses configurable
            if encounter.get_boss() != Rockgrove.OAXILTSO:
                continue
        except NotImplementedError:
            continue

        # Use the trial of the first encounter for the log title
        if not log_trial_name:
            log_trial_name = encounter.trialId.name.capitalize()

        # Compute debuff uptimes
        encounter.compute_debuff_uptimes()

        # Render all data about the encounter
        encounters_html.append(render_encounter(encounter, debuffs=debuffs, hostile_units=hostile_units))

    title_timestamp = encounter_log.begin_log.time.strftime("%d.%m.%Y (%H:%M:%S)")
    log_title = f"{config.export.title_prefix} - {log_trial_name} - {title_timestamp}"

    timestamp = encounter_log.begin_log.time.strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"{config.export.path}/{log_trial_name.lower()}_{timestamp}_{config.export.file_suffix}.html"

    return render_to_file("log", {
        "title": log_title,
        "encounters": encounters_html,
        "url_prefix": config.web.url_prefix
    }, file_name)


def render_encounter(encounter: CombatEncounter, hostile_units: List[str] = None, debuffs: List[str] = None) -> str:
    # TODO: counter of wipes/clears
    boss_name = encounter.get_boss().value
    boss_unit = [unit for unit in encounter.boss_units if unit.unit.name == boss_name][0]
    is_clear = all([unit.was_killed for unit in encounter.boss_units])
    final_boss_hp = float(boss_unit.uptime_end_event.target_current_health) / float(boss_unit.uptime_end_event.target_maximum_health)
    # Don't show boss hp if it was a clear
    final_boss_hp = "" if is_clear else f" - {format_uptime(final_boss_hp)[0]}"
    encounter_title = f"{boss_name} - {format_time(encounter.event_span.duration)}{final_boss_hp} - ({encounter.begin.time.strftime('%H:%M:%S')})"

    # TODO: dps
    # TODO: buff uptimes
    # TODO: mechanic stats
    # TODO: special uptimes

    debuff_table = __render_debuff_table(encounter=encounter, units=hostile_units, abilities=debuffs)

    return __render_encounter(title=encounter_title, debuff_table=debuff_table, is_clear=is_clear)


def __render_debuff_table(encounter: CombatEncounter, units: List[str] = None, abilities: List[str] = None):
    header_row: List[str] = [__NAME_KEY]
    rows: List[Dict[str, Cell]] = []

    units = [unit for unit in encounter.hostile_units if unit.unit.name in units]

    target_active_times = {
        __NAME_KEY: Cell("Active time of each target")
    }
    for unit in units:
        header_row.append(unit.display_str)
        active_time_str = f"{format_time(unit.uptime_begin, encounter)} to {format_time(unit.uptime_end, encounter)} ({format_time(unit.duration)})"
        # Use the uptime colors (green=died, red=alive)
        color = format_uptime(unit.was_killed)[1]
        target_active_times[unit.display_str] = Cell(value=active_time_str, color=color)

    for ability_name in abilities:
        row = {
            __NAME_KEY: Cell(ability_name)
        }
        for unit in units:
            relative_uptime = unit.relative_uptime_for_ability_name(ability_name)
            total_uptime = unit.uptime_for_ability_name(ability_name)
            percent_str, color = format_uptime(relative_uptime)
            row[unit.display_str] = Cell(value=f"{percent_str} ({format_time(total_uptime)})", color=color)

        rows.append(row)

    return __render_table(title="Debuff uptimes", header_row=header_row, active_row=target_active_times, rows=rows)
