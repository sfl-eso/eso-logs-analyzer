from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Union, List, Dict

from tqdm import tqdm

from utils import read_csv, get_num_lines
from .events import Event, EndLog, EffectInfo, BeginCast, BeginLog, AbilityInfo, EndCast
from .events.enums import CastStatus


class EncounterLog(object):

    def __init__(self, events: List[Event]):
        self._events = events

        # Sort the events by their type
        event_dict = defaultdict(list)
        for event in events:
            event_dict[event.event_type].append(event)
        # Create a dictionary that throws errors if non-existing keys are read
        self._event_dict = dict(event_dict)

        # Meta events
        assert len(self._event_dict[BeginLog.event_type]) == 1, f"More than one {BeginLog.event_type} event in encounterlog!"
        assert len(self._event_dict[EndLog.event_type]) == 1, f"More than one {EndLog.event_type} event in encounterlog!"
        self.begin_log: BeginLog = self._event_dict[BeginLog.event_type][0]
        self.end_log: EndLog = self._event_dict[EndLog.event_type][0]

        # Gather ability and effect info events and enrich them with each other
        self.ability_infos: Dict[int, AbilityInfo] = {ability_info.ability_id: ability_info
                                                      for ability_info in self._event_dict[AbilityInfo.event_type]}
        self.effect_infos: Dict[int, EffectInfo] = {effect_info.ability_id: effect_info
                                                    for effect_info in self._event_dict[EffectInfo.event_type]}

        for event in tqdm(self._events, "Resolving event references"):
            event.compute_event_time(self)
            event.resolve_ability_and_effect_info_references(self)

        self.match_cast_events()

        # # Unit spawns and kills
        # self._match_unit_events()
        # # self._unit_infos: Dict[tuple, List[UnitAdded]] = defaultdict(list)
        # # for unit_added in self._event_dict["UNIT_ADDED"]:
        # #     self._unit_infos[(unit_added.id, unit_added.unit_id)].append(unit_added)
        # # self._unit_infos = dict(self._unit_infos)
        #
        # # Combat encounters
        # self.player_infos: Dict[str, UnitAdded] = {unit_info.unit_id: unit_info
        #                                            for unit_info in self._event_dict["UNIT_ADDED"]
        #                                            if unit_info.unit_type == "PLAYER"}
        # self.combat_encounters: List[BeginCombat] = []
        # self._create_combat_encounters()
        # for encounter in tqdm(self.combat_encounters, desc="Initializing encounters"):
        #     # First check that we won't get unit id collisions in this encounter
        #     encounter.check_unit_overlap()
        #     # Extract all hostile units that are active during this encounter
        #     encounter.extract_hostile_units()
        #
        # self._merge_combat_encounters()
        #
        # for encounter in tqdm(self.combat_encounters, desc="Enriching combat events"):
        #     encounter.enrich_combat_events()

    def __str__(self):
        return f"{self.__class__.__name__}(begin={self.begin_log.time}, end={self.end_log.time})"

    __repr__ = __str__

    def match_cast_events(self):
        # The cache will be used to confirm that every cast was ended, and the dict is just needed for lookups of duplicate end cast events
        begin_cast_cache: Dict[str, BeginCast] = {}
        begin_cast_dict: Dict[str, BeginCast] = {}

        for event in tqdm(self._events, desc="Matching cast events"):
            if isinstance(event, BeginCast):
                begin_cast_cache[event.cast_effect_id] = event
                begin_cast_dict[event.cast_effect_id] = event
            elif isinstance(event, EndCast):
                try:
                    begin_event = begin_cast_dict[event.cast_effect_id]
                except KeyError:
                    # TODO: logging
                    # logger().warn(f"No begin cast for end cast {event}")
                    continue
                event.begin_cast = begin_event
                if event.status == CastStatus.COMPLETED and begin_event.end_cast is not None:
                    begin_event.duplicate_end_casts.append(event)
                elif event.status == CastStatus.COMPLETED:
                    begin_event.end_cast = event
                    del begin_cast_cache[event.cast_effect_id]
                elif event.status == CastStatus.PLAYER_CANCELLED or event.status == CastStatus.INTERRUPTED:
                    begin_event.cancelled_end_cast = event

        if len(begin_cast_cache) > 0:
            pass
            # TODO: logging
            # logger().warn(f"Found {len(begin_cast_cache)} begin events without end")

    @classmethod
    def parse_log(cls, file: Union[str, Path], multiple: bool = False) -> Union[EncounterLog, List[EncounterLog]]:
        """
        Parses an encounterlog file into one or multiple logs depending on the passed parameters and how many
        logs are contained in the file.
        """
        path = Path(file)
        path = path.absolute()
        num_lines = get_num_lines(file)
        csv_file = read_csv(str(path), has_header=False)
        events = []
        count = 0
        logs = []
        previous_event = None

        for line in tqdm(csv_file, desc=f"Parsing log {path}", total=num_lines):
            # Convert the line into an event object
            event = Event.create(count, int(line[0]), line[1], *line[2:])

            # Connect the event linked list pointers
            if previous_event is not None:
                event.previous = previous_event
            events.append(event)
            previous_event = event
            # Increase the line number count for debugging purposes
            count += 1

            # Separate logs into different objects if there are multiple logs in the file
            if isinstance(event, EndLog):
                logs.append(events)
                if multiple:
                    # We have a separate log starting after this line
                    events = []
                    count = 0
                    previous_event = None
                else:
                    break

        # Convert the events into EncounterLog objects
        logs = [cls(events) for events in logs]
        return logs if multiple else logs[0]
