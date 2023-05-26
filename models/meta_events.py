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

    # 3,BEGIN_LOG,1614974057994,15,"EU Megaserver","en","eso.live.6.2"
    def __init__(self, id: int, epoch_time: str, unknown: str, server: str, locale: str, client_version: str):
        """
        :param unknown: Some kind of integer
        """
        super(BeginLog, self).__init__(id, unknown)
        self.time = parse_epoch_time(epoch_time)
        self.server = server
        self.locale = locale
        self.client_version = client_version

    def event_time(self, event_id: int) -> datetime:
        return self.time + timedelta(milliseconds=(event_id - self.id))


class EndLog(Event):
    event_type: str = "END_LOG"

    def __init__(self, id: int):
        super(EndLog, self).__init__(id)


class BeginTrial(Event):
    event_type: str = "BEGIN_TRIAL"

    def __init__(self, id: int, unknown: str, epoch_time: str):
        """
        :param unknown: Some kind of integer
        """
        super(BeginTrial, self).__init__(id, unknown)
        self.time = parse_epoch_time(epoch_time)

    def event_time(self, event_id: int) -> datetime:
        return self.time + timedelta(milliseconds=(event_id - self.id))


class EndTrial(Event):
    event_type: str = "END_TRIAL"

    # 7094915,END_TRIAL,13,6441656,T,78964,0
    def __init__(self, id: int, unknown1: str, unknown2: str, unknown3: str, unknown4: str, unknown5: str):
        """
        :param unknown1: Some kind of integer
        :param unknown2: Some kind of integer
        :param unknown3: Some kind of char 'T' (maybe boolean?)
        :param unknown4: Some kind of integer
        :param unknown5: Some kind of integer (usually 0)
        """
        super(EndTrial, self).__init__(id)


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

            # Distinguish different event types (TODO: maybe do this in UnitAdded)
            # if isinstance(event, CombatEvent):
            #     if event.target_unit.hostility == "PLAYER_ALLY" and event.unit.hostility == "HOSTILE":
            #         # Damage taken
            #         self.damage_taken_events.append(event)
            #     elif event.target_unit.hostility == "HOSTILE" and event.unit.hostility == "PLAYER_ALLY":
            #         # Damage done
            #         self.damage_done_events.append(event)
            # elif isinstance(event, EffectChanged):
            #     if event.target_unit.hostility == "PLAYER_ALLY" and event.unit.hostility == "HOSTILE":
            #         # Debuffs taken
            #         self.debuff_taken_events.append(event)
            #         pass
            #     elif event.target_unit.hostility == "HOSTILE" and event.unit.hostility == "PLAYER_ALLY":
            #         # Debuffs done
            #         self.debuff_events.append(event)
            #     elif event.target_unit.hostility == "PLAYER_ALLY" and event.unit.hostility == "PLAYER_ALLY":
            #         # Buffs done/taken
            #         self.buff_events.append(event)

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

    def __init__(self, id: int, map_id: str, map_name: str, map_icon: str):
        super(MapChanged, self).__init__(id)
        self.map_id = map_id
        self.map_name = map_name
        self.map_icon = map_icon


class TrialInit(Event):
    event_type: str = "TRIAL_INIT"

    def __init__(self, id: int, unknown1, unknown2, unknown3, epoch_time: str, unknown4, unknown5, unknown6):
        """
        :param unknown1: Some kind of id
        :param unknown2: 'T' or 'F'
        :param unknown3: 'T' or 'F'
        :param unknown4: Some kind of id (e.g. '161534')
        :param unknown5: 'T' or 'F'
        :param unknown6: Integer (e.g., '0')
        """
        super(TrialInit, self).__init__(id, unknown1, unknown2, unknown3, unknown4, unknown5, unknown6)
        self.time = parse_epoch_time(epoch_time)
