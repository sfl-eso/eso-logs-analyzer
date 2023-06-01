from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Union, List, Dict, Type, Set

from tqdm import tqdm

from .events import Event, EndLog, EffectInfo, BeginCast, BeginLog, AbilityInfo, EndCast, UnitAdded, UnitChanged, UnitRemoved, BeginTrial, EndTrial, BeginCombat, EndCombat, \
    TargetEvent
from .events.enums import UnitType, CastStatus, TrialId
from ..base import Base
from ...utils import read_csv, get_num_lines


class EncounterLog(Base):

    def __init__(self, tqdm_index: int, *args, **kwargs):
        """
        Creates an encounter log object. Most instance variables are only declared, but not initialized with a value, since this object needs to be
        created and passed to each event that is part of it. The data will be filled at a later point.
        @param tqdm_index: If set to a non-zero value, this method happens in a parallel context and the tqdm progress bar needs to be adjusted.
        """
        super().__init__(*args, **kwargs)

        self.__tqdm_index = tqdm_index

        self.events: List[Event] = None
        self._event_dict: Dict[str, List[Event]] = None
        self.begin_log: BeginLog = None
        self.end_log: EndLog = None
        self.ability_infos: Dict[int, AbilityInfo] = None
        self.valid_ability_names = None
        self.effect_infos: Dict[int, EffectInfo] = None
        self.player_unit_added: Dict[int, UnitAdded] = None

    def initialize(self, events: List[Event]):
        self.events = events

        # Sort the events by their type
        event_dict = defaultdict(list)
        for event in self.events:
            event_dict[event.event_type].append(event)
        # Create a dictionary that throws errors if non-existing keys are read
        self._event_dict = dict(event_dict)

        # Ensure that there is only a single begin and end log event in this encounter log.
        assert len(self._event_dict[BeginLog.event_type]) == 1, f"More than one {BeginLog.event_type} event in encounterlog!"
        assert len(self._event_dict[EndLog.event_type]) == 1, f"More than one {EndLog.event_type} event in encounterlog!"
        self.begin_log: BeginLog = self._event_dict[BeginLog.event_type][0]
        self.end_log: EndLog = self._event_dict[EndLog.event_type][0]

        # Gather events by their identifying ids
        self.ability_infos: Dict[int, AbilityInfo] = {ability_info.ability_id: ability_info for ability_info in self._event_dict[AbilityInfo.event_type]}
        self.valid_ability_names = set([ability.name for ability in self.ability_infos.values()])
        self.effect_infos: Dict[int, EffectInfo] = {effect_info.ability_id: effect_info for effect_info in self._event_dict[EffectInfo.event_type]}
        self.player_unit_added: Dict[int, UnitAdded] = {unit.unit_id: unit for unit in self._event_dict[UnitAdded.event_type]
                                                        if unit.unit_type == UnitType.PLAYER}

        for event in tqdm(self.events, "Resolving event references", position=self.__tqdm_index, leave=not self.__tqdm_index):
            event.compute_event_time(self)
            event.resolve_ability_and_effect_info_references(self)

        # Match the span events with their end-counterparts and set the begin and end event fields.
        self.__match_cast_events()
        self.__match_combat_events()
        self.__match_log_events()
        self.__match_trial_events()
        self.__match_unit_events()

    def __str__(self):
        return f"{self.__class__.__name__}(begin={self.begin_log.time}, end={self.end_log.time})"

    __repr__ = __str__

    def __match_cast_events(self):
        """
        Match casts that are separated into a being and end cast event.
        """

        def structure_cast_events(cast_type: Type[Event]) -> dict:
            """
            Structures the cast events in a format cast_effect_id -> ability_id -> list of events
            """
            structured_events: Dict[int, Dict[int, List[Event]]] = defaultdict(lambda: defaultdict(list))
            for cast_event in self._event_dict[cast_type.event_type]:
                structured_events[cast_event.cast_effect_id][cast_event.ability_id].append(cast_event)
            # Remove defaultdict functionality
            return {cast_effect_id: dict(data) for cast_effect_id, data in structured_events.items()}

        def match_events(begin_cast: BeginCast, end_cast: EndCast):
            """
            Sets the appropriate fields to match two events
            """
            begin_cast.end_cast = end_cast
            end_cast.begin_casts.append(begin_cast)

        begin_event_dict: Dict[int, Dict[int, List[BeginCast]]] = structure_cast_events(BeginCast)
        end_event_dict: Dict[int, Dict[int, List[EndCast]]] = structure_cast_events(EndCast)

        cast_effect_ids: Set[int] = set(begin_event_dict.keys()).union(set(end_event_dict.keys()))

        missing_end_casts = []
        missing_begin_casts = []
        # Contains end cast events for which there is no begin cast event with the same cast effect id and ability id
        missing_ability_id_begin_casts: Dict[int, List[EndCast]] = defaultdict(list)

        for cast_effect_id in tqdm(cast_effect_ids, desc="Matching cast events", position=self.__tqdm_index, leave=not self.__tqdm_index):
            if cast_effect_id not in begin_event_dict:
                # The begin cast event for this cast was not recorded.
                missing_begin_casts.append(cast_effect_id)
                continue

            if cast_effect_id not in end_event_dict:
                # The end cast event for this cast was not recorded.
                missing_end_casts.append(cast_effect_id)
                continue

            ability_ids: Set[int] = set(begin_event_dict[cast_effect_id].keys()).union(set(end_event_dict[cast_effect_id].keys()))

            for ability_id in ability_ids:
                if ability_id not in begin_event_dict[cast_effect_id]:
                    # This case happens when a cast applies multiple ability ids that have separate end cast events.
                    missing_ability_id_begin_casts[cast_effect_id].extend(end_event_dict[cast_effect_id][ability_id])
                    continue

                if ability_id not in end_event_dict[cast_effect_id]:
                    self.logger.error(f"No end cast event found for cast effect id {cast_effect_id} and ability id {ability_id}")
                    continue

                begin_events = begin_event_dict[cast_effect_id][ability_id]
                end_events = end_event_dict[cast_effect_id][ability_id]
                if len(begin_events) == 1 and len(end_events) == 1:
                    # There is only a single begin event and a single end event for this cast and ability.
                    match_events(begin_events[0], end_events[0])
                elif len(begin_events) > 1 and len(end_events) == 1:
                    # There are multiple begin casts that share an end cast.
                    # This is the case with actions that trigger multiple cast events with different effects that all finished with the same state.
                    for begin_event in begin_events:
                        match_events(begin_event, end_events[0])
                elif len(begin_events) == 1 and len(end_events) > 1:
                    # Sometimes there are cancelled and completed end cast events for the same begin cast.
                    # Ignore the cancelled event cast in this case
                    completed_end_events = [event for event in end_events if event.status == CastStatus.COMPLETED]
                    if len(completed_end_events) > 0:
                        end_event = max(completed_end_events)
                        match_events(begin_events[0], end_event)
                    else:
                        # This case should not happen, but handle it in case it does
                        self.logger.error(f"No completed cast event found for cast effect id {cast_effect_id} with multiple end events")
                        end_event = max(end_events)
                        match_events(begin_events[0], end_event)
                elif len(begin_events) == 2 and len(end_events) == 2:
                    # Two casts are triggered by the same action and they finish in different states.
                    # The begin cast event with the shorter cast duration was finished and the one with the longer duration was cancelled.
                    begin_events = sorted(begin_events, key=lambda e: e.duration)
                    completed_begin_event = begin_events[0]
                    cancelled_begin_event = begin_events[1]
                    try:
                        completed_end_event = [event for event in end_events if event.status == CastStatus.COMPLETED][0]
                        cancelled_end_event = [event for event in end_events if event.status != CastStatus.COMPLETED][0]
                        match_events(completed_begin_event, completed_end_event)
                        match_events(cancelled_begin_event, cancelled_end_event)
                    except IndexError as e:
                        # TODO: these are only unique within a single trial instance
                        self.logger.error(f"Error matching casts for effect cast id {cast_effect_id} and ability id {ability_id}: {e}")

                    if len(begin_events) > 2:
                        self.logger.error(f"More than 2 events for effect cast id {cast_effect_id} and ability id {ability_id}")
                elif len(begin_events) == len(end_events):
                    # There are more than two different finished states for the end cast events.
                    end_cast_states = [event.status for event in end_events]
                    self.logger.error(
                        f"End cast events have more than two different result states ({end_cast_states}) for cast effect id {cast_effect_id} and ability id {ability_id}")
                else:
                    # There are different amounts of begin and end cast events. This should never occur
                    self.logger.error(f"Different amounts of begin and end cast events found for cast effect id {cast_effect_id} and ability id {ability_id}")

        if missing_begin_casts:
            self.logger.info(f"{len(missing_begin_casts)} end cast events did not have matching begin cast events.")

        if missing_end_casts:
            self.logger.info(f"{len(missing_end_casts)} begin cast events did not have matching end cast events.")

        if missing_ability_id_begin_casts:
            # Match end cast events for which there was no matching ability id with begin cast events of the same effect cast id but a different ability id.
            # Only match up end cast events, if there is only a single viable begin cast event that it can be attached to.
            num_unmatched_orphaned_end_casts = 0
            for cast_effect_id, orphaned_end_casts in missing_ability_id_begin_casts.items():
                ability_id_to_begin_cast_dict = begin_event_dict[cast_effect_id]
                if len(ability_id_to_begin_cast_dict) == 1:
                    # Only match orphaned end cast event if there is only a single ability id in the begin casts dict for this cast effect id
                    ability_id = list(ability_id_to_begin_cast_dict.keys())[0]
                    begin_cast_events = ability_id_to_begin_cast_dict[ability_id]
                    if len(begin_cast_events) == 1:
                        # Only match orphaned end cast event if there is only a single begin cast event candidate
                        begin_cast_event = begin_cast_events[0]
                        begin_cast_event.orphaned_end_casts.extend(orphaned_end_casts)
                        for end_cast_event in orphaned_end_casts:
                            end_cast_event.begin_casts.append(begin_cast_event)
                    else:
                        num_unmatched_orphaned_end_casts += 1
                        self.logger.debug(f"Skipping orphaned end casts for cast effect id {cast_effect_id} and ability id {ability_id} due to multiple viable begin cast events")
                else:
                    num_unmatched_orphaned_end_casts += 1
                    self.logger.debug(f"Skipping orphaned end casts for cast effect id {cast_effect_id} due to multiple viable begin cast ability ids")

            if num_unmatched_orphaned_end_casts:
                self.logger.info(f"{num_unmatched_orphaned_end_casts} orphaned end cast events could not be matched to begin cast events with the same cast effect id.")

    def __match_combat_events(self):
        """
        Match begin combat encounters to their end events. Since combat happens sequentially these events should always happen sequentially as well.
        """
        current_encounter: BeginCombat = None
        for event in tqdm(self.events, desc="Matching combat events", position=self.__tqdm_index, leave=not self.__tqdm_index):
            if isinstance(event, BeginCombat):
                if current_encounter is not None:
                    self.logger.error(f"Entering combat event {event} while already in combat event {current_encounter}")
                current_encounter = event

            elif isinstance(event, EndCombat):
                if current_encounter is None:
                    self.logger.error(f"Leaving combat event {event} without being in combat")
                    continue

                event.begin_combat = current_encounter
                current_encounter.end_combat = event
                current_encounter = None

    def __match_log_events(self):
        """
        Connect the begin and end log events with each other.
        """
        self.begin_log.end_log = self.end_log
        self.end_log.begin_log = self.begin_log

    def __match_trial_events(self):
        """
        Match trial events to their respective end trial events.
        If a trial was not finished, there won't be a matching end trial event.
        """

        begin_trial_cache: Dict[TrialId, BeginTrial] = {}
        last_begin_trial: BeginTrial = None
        for event in tqdm(self.events, desc="Matching trial events", position=self.__tqdm_index, leave=not self.__tqdm_index):
            if isinstance(event, BeginTrial):
                if event.trial_id in begin_trial_cache:
                    self.logger.info(
                        f"Existing begin trial event at line {begin_trial_cache[event.trial_id].id + 1} for trial {event.trial_id} has no matching end trial event.")
                begin_trial_cache[event.trial_id] = event
                last_begin_trial = event
            elif isinstance(event, EndTrial):
                last_begin_trial = None
                if event.trial_id in begin_trial_cache:
                    begin_event = begin_trial_cache[event.trial_id]
                    event.begin_trial = begin_event
                    begin_event.end_trial = event
                else:
                    self.logger.warning(f"No matching begin trial event found for end trial event at line {event.id + 1} for trial {event.trial_id}.")
            elif isinstance(event, BeginCombat):
                event.begin_trial = last_begin_trial

    def __match_unit_events(self):
        """
        Match unit events of their spawn, changes and when they are removed.
        Unit ids of removed units may be reused for different units later on. Thus, we need to iterate over the events in their order.
        """
        added_units = {}
        # Note: no need to use tqdm to monitor progress here, since this does not require a lot of time.
        for event in self.events:
            if isinstance(event, UnitAdded):
                if event.unit_id in added_units:
                    self.logger.error(f"Duplicate unit added event with id {event.event_id}")
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
            elif isinstance(event, TargetEvent):
                # For any event that contains unit information, we can enrich the unit fields now, since we track all units that are alive at the moment
                # of the target event happening
                if event.unit_id in added_units:
                    event.unit = added_units[event.unit_id]
                elif event.unit_id:
                    self.logger.error(f"No unit found for event {event} with unit id {event.unit_id}")
                if event.target_unit_id is not None and event.target_unit_id in added_units:
                    event.target_unit = added_units[event.target_unit_id]
                elif event.target_unit_id:
                    self.logger.error(f"No unit found for event {event} with target unit id {event.target_unit_id}")

    def events_for_type(self, event_type: Type[Event]):
        return self._event_dict[event_type.event_type]

    @classmethod
    def parse_log(cls, file: Union[str, Path], multiple: bool = False, tqdm_index: int = 0) -> Union[EncounterLog, List[EncounterLog]]:
        """
        Parses an encounterlog file into one or multiple logs depending on the passed parameters and how many logs are contained in the file.
        @param file: File containing the encounter log data.
        @param multiple: If set to True, if multiple logs are in a single file, they will be loaded and their encounters chained together.
        @param tqdm_index: If set to a non-zero value, this method happens in a parallel context and the tqdm progress bar needs to be adjusted.
        @return: A single or multiple encounter log objects, depending on the number of logs in the input file.
        """
        path = Path(file)
        path = path.absolute()
        num_lines = get_num_lines(file)
        csv_file = read_csv(str(path), has_header=False)
        events = []
        current_id = 0
        logs = []
        previous_event = None

        current_log = EncounterLog(tqdm_index)

        for line in tqdm(csv_file, desc=f"Parsing log {path}", total=num_lines, position=tqdm_index, leave=not tqdm_index):

            # Convert the line into an event object
            try:
                event = Event.create(current_id, current_log, int(line[0]), line[1], *line[2:])
            except ValueError as e:
                cls.logger.error(f"Could not create Event of type {line[1]} at line {current_id + 1}! {e}")
                continue
            finally:
                current_id += 1

            # Connect the event linked list pointers
            # if previous_event is not None:
            #     event.previous = previous_event
            events.append(event)
            # previous_event = event

            # Separate logs into different objects if there are multiple logs in the file
            if isinstance(event, EndLog):
                current_log.initialize(events)
                logs.append(current_log)
                if multiple:
                    # We have a separate log starting after this line
                    events = []
                    current_id = 0
                    current_log = EncounterLog(tqdm_index)
                else:
                    break

        return logs if multiple else logs[0]
