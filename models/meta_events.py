from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING

from logger import logger
from utils import parse_epoch_time
from .event import Event
from .unit_events import UnitAdded
from .ability_events import TargetEvent, HealthRegen, EffectChanged, EndCast, CombatEvent

if TYPE_CHECKING:
    from .log import EncounterLog


class BeginLog(Event):
    event_type: str = "BEGIN_LOG"

    def __init__(self, id: int, epoch_time: str, log_version: str, server: str, locale: str, client_version: str):
        super(BeginLog, self).__init__(id)
        self.time = parse_epoch_time(epoch_time)
        self.server = server
        self.locale = locale
        self.client_version = client_version
        self.log_version = log_version

    def event_time(self, event_id: int) -> datetime:
        return self.time + timedelta(milliseconds=(event_id - self.id))


class EndLog(Event):
    event_type: str = "END_LOG"

    def __init__(self, id: int):
        super(EndLog, self).__init__(id)


class BeginTrial(Event):
    """
    Technically the epoch time is "startTimeMS"
    """

    event_type: str = "BEGIN_TRIAL"

    def __init__(self, id: int, trial_id: str, epoch_time: str):
        super(BeginTrial, self).__init__(id)
        self.time = parse_epoch_time(epoch_time)
        self.trial_id = trial_id
        self.end_trial: EndTrial = None

    def event_time(self, event_id: int) -> datetime:
        return self.time + timedelta(milliseconds=(event_id - self.id))


class EndTrial(Event):
    event_type: str = "END_TRIAL"

    def __init__(self, id: int, trial_id: str, trial_duration_ms: str, success: str, final_score: str, final_vitality_bonus: str):
        super(EndTrial, self).__init__(id)
        self.trial_id = trial_id
        self.trial_duration_ms = int(trial_duration_ms)
        self.success = success == "T"
        self.final_score = final_score
        self.final_vitality_bonus = final_vitality_bonus


class BeginCombat(Event):
    event_type: str = "BEGIN_COMBAT"

    def __init__(self, id: int):
        super(BeginCombat, self).__init__(id)
        self.end_combat: EndCombat = None
        self.events: List[Event] = []

        # Units that are alive/active as the encounter starts
        self.start_units: List[UnitAdded] = []
        # Units that are alive/active during the encounter
        self.active_units: List[UnitAdded] = []
        # Units that are alive/active as the encounter ends
        self.end_units: List[UnitAdded] = []
        # All enemy units that appear during the encounter
        self.hostile_units: List[UnitAdded] = []

        self.buff_events: list = []
        self.debuff_events: list = []
        self.debuff_taken_events: list = []
        self.damage_done_events: list = []
        self.damage_taken_events: list = []

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, end_combat={self.end_combat is not None}, " \
               f"events={len(self.events)})"

    __repr__ = __str__

    def extract_hostile_units(self):
        self.hostile_units = [unit for unit in self.active_units if unit.hostility == "HOSTILE"]

    def process_combat_events(self):
        unit_dict = {event.unit_id: event for event in self.active_units}

        for event in self.events:
            # Set unit field for values referencing a unit
            try:
                if isinstance(event, TargetEvent):
                    unit = unit_dict[event.unit_id]
                    if unit is not None:
                        unit.combat_events_source[self].append(event)
                        event.unit = unit
                    target_unit = unit_dict[event.target_unit_id]
                    if target_unit is not None:
                        target_unit.combat_events_target[self].append(event)
                        event.target_unit = target_unit
                elif isinstance(event, HealthRegen):
                    unit = unit_dict[event.unit_id]
                    unit.health_regen_events[self].append(event)
                    event.unit = unit
            except KeyError:
                logger().warn(f"Skipping event {event} with unit id {event.unit_id} for which no unit can be found")

    def check_unit_overlap(self):
        # Check that there are no units that are different but share a unit id in this encounter
        unique_units = set(self.start_units).union(set(self.end_units)).union(set(self.active_units))
        unique_unit_ids = set([event.unit_id for event in unique_units])
        assert len(unique_units) == len(unique_unit_ids), f"Encounter contains multiple units with the same unit id: {self}"

        # Confirm that the active unit list contains all units that are in the start and end units
        start_end = set(self.start_units).union(set(self.end_units))
        non_active_units = start_end.difference(set(self.active_units))
        assert len(non_active_units) == 0, f"Encounter has start or end units than are not listed as active: {self}"

    # def compute_uptimes(self, log: EncounterLog):
    #     # Keep track of data in the form of Dict(unit_id -> Dict(ability_id -> object))
    #     tracker = defaultdict(dict)
    #     for event in self.events:
    #         if not isinstance(event, EffectChanged):
    #             continue
    #         if event.ability.effect_info.effect_type != "DEBUFF" or event.target_unit_id is None:
    #             continue
    #         if event.status == "GAINED":
    #             tracker[event.target_unit_id][event.ability_id] = event
    #         elif event.status == "FADED":
    #             if event.ability_id in tracker[event.target_unit_id]:
    #                 gained_event = tracker[event.target_unit_id][event.ability_id]
    #                 event.gained_event = gained_event
    #                 gained_event.faded_event = event
    #                 del tracker[event.target_unit_id][event.ability_id]
    #             else:
    #                 print(f"No match found for event {event.id}")
    #         elif event.status == "UPDATED":
    #             pass


class EndCombat(Event):
    event_type: str = "END_COMBAT"

    def __init__(self, id: int):
        super(EndCombat, self).__init__(id)
        self.begin_combat: BeginCombat = None

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, begin_combat={self.begin_combat is not None})"

    __repr__ = __str__


class ZoneChanged(Event):
    event_type: str = "ZONE_CHANGED"

    def __init__(self, id: int, zone_id: str, zone_name: str, difficulty: str):
        super(ZoneChanged, self).__init__(id)
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.difficulty = difficulty


class MapChanged(Event):
    event_type: str = "MAP_CHANGED"

    def __init__(self, id: int, map_id: str, map_name: str, texture_path: str):
        super(MapChanged, self).__init__(id)
        self.map_id = map_id
        self.map_name = map_name
        self.map_icon = texture_path


class TrialInit(Event):
    event_type: str = "TRIAL_INIT"

    def __init__(self, id: int, trial_id: str, in_progress: str, completed: str, start_time_in_ms: str, duration_in_ms, success: str, final_score: str):
        super(TrialInit, self).__init__(id)
        self.trial_id = trial_id
        self.in_progress = in_progress == "T"
        self.completed = completed == "T"
        self.start_time_in_ms = int(start_time_in_ms)
        self.duration_in_ms = int(duration_in_ms)
        self.success = success == "T"
        self.final_score = final_score
