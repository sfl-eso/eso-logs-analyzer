from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Union, List, Dict

from utils import read_csv, get_num_lines, tqdm
from .events import Event, EndLog, EffectInfo, BeginCast, BeginLog, AbilityInfo, EndCast, UnitAdded, UnitChanged, UnitRemoved
from .events.enums import UnitType
from ..base import Base


class EncounterLog(Base):

    def __init__(self, events: List[Event]):
        super().__init__()

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

        # Gather events by their identifying ids
        self.ability_infos: Dict[int, AbilityInfo] = {ability_info.ability_id: ability_info for ability_info in self._event_dict[AbilityInfo.event_type]}
        self.effect_infos: Dict[int, EffectInfo] = {effect_info.ability_id: effect_info for effect_info in self._event_dict[EffectInfo.event_type]}
        self.player_unit_added: Dict[int, UnitAdded] = {unit.unit_id: unit for unit in self._event_dict[UnitAdded.event_type]
                                                        if unit.unit_type == UnitType.PLAYER}

        for event in tqdm(self._events, "Resolving event references"):
            event.compute_event_time(self)
            event.resolve_ability_and_effect_info_references(self)

        self._match_cast_events()
        self._match_unit_events()

        # # Combat encounters
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

    def _match_cast_events(self):
        """
        Match casts that are separated into a being and end cast event.
        """
        # The cache will be used to confirm that every cast was ended, and the dict is just needed for lookups of duplicate end cast events
        begin_cast_cache: Dict[str, BeginCast] = {}
        begin_cast_dict: Dict[str, BeginCast] = {}

        for event in tqdm(self._events, desc="Matching cast events"):
            if isinstance(event, BeginCast):
                # TODO: there can be multiple begin cast events with the same ids
                # TODO: use the time to match them up
                begin_cast_cache[event.cast_effect_id] = event
                begin_cast_dict[event.cast_effect_id] = event
            elif isinstance(event, EndCast):
                try:
                    begin_event: BeginCast = begin_cast_dict[event.cast_effect_id]
                except KeyError:
                    self.logger.warning(f"No begin cast for end cast {event}")
                    continue
                event.begin_cast = begin_event

                if event.ability_id == begin_event.ability_id:
                    if begin_event.end_cast is not None:
                        self.logger.error(f"Multiple end cast events with matching ability id for {begin_event}")
                        begin_event.duplicate_end_casts.append(event)
                    else:
                        begin_event.end_cast = event
                else:
                    begin_event.duplicate_end_casts.append(event)

        for begin_event in begin_cast_cache.values():
            if begin_event.end_cast is None and len(begin_event.duplicate_end_casts) == 0:
                self.logger.warning(f"No end cast found for begin cast {begin_event}")
            elif begin_event.end_cast is None:
                self.logger.error(
                    f"No end cast found with matching ability id found for begin cast {begin_event} but {len(begin_event.duplicate_end_casts)} other end cast events were found")

    def _match_unit_events(self):
        """
        Match unit events of their spawn, changes and when they are removed.
        Unit ids of removed units may be reused for different units later on. Thus, we need to iterate over the events in their order.
        """
        added_units = {}
        for event in tqdm(self._events, desc="Matching unit events"):
            if isinstance(event, UnitAdded):
                if event.unit_id in added_units:
                    self.logger.error(f"Duplicate unit added event with id {event.id}")
                else:
                    added_units[event.unit_id] = event
            elif isinstance(event, UnitRemoved):
                unit_added = added_units[event.unit_id]
                unit_added.unit_removed = event
                event.unit_added = unit_added
                del added_units[event.unit_id]
            elif isinstance(event, UnitChanged):
                unit_added = added_units[event.unit_id]
                unit_added.unit_changed.append(event)
                event.unit_added = unit_added

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
            try:
                event = Event.create(count, int(line[0]), line[1], *line[2:])
            except ValueError as e:
                cls.logger.error(f"Could not create Event of type {line[1]} at line {count + 1}! {e}")
                continue
            finally:
                count += 1

            # Connect the event linked list pointers
            if previous_event is not None:
                event.previous = previous_event
            events.append(event)
            previous_event = event
            # Increase the line number count for debugging purposes

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
