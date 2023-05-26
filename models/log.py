from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm

from models import Event, AbilityInfo, BeginLog, EndLog, BeginCombat, EndCombat, EffectInfo, PlayerInfo, UnitAdded, \
    UnitRemoved, UnitChanged, TrialInit
from utils import read_csv


class EncounterLog(object):
    def __init__(self, events: List[Event]):
        self._events = events

        # Create dict for convenience
        event_dict = defaultdict(list)
        for event in events:
            event_dict[event.event_type].append(event)
        self._event_dict = dict(event_dict)

        # Meta events
        self._begin_log: BeginLog = self._event_dict["BEGIN_LOG"][0]
        self._end_log: EndLog = self._event_dict["END_LOG"][0]

        # Set the epoch time for each event by computing the diff to the begin log event
        for event in self._events:
            if not isinstance(event, TrialInit):
                event.time = self._begin_log.event_time(event.id)

        # Ability Infos
        self.ability_infos: Dict[str, AbilityInfo] = {ability_info.ability_id: ability_info
                                                      for ability_info in self._event_dict["ABILITY_INFO"]}
        # self._ability_infos_by_name = {ability_info.name: ability_info
        #                                for ability_info in self._event_dict["ABILITY_INFO"]}
        self._match_event_infos()

        # Unit spawns and kills
        self._match_unit_events()
        self._unit_infos: Dict[str, List[UnitAdded]] = defaultdict(list)
        for unit_added in self._event_dict["UNIT_ADDED"]:
            self._unit_infos[unit_added.unit_id].append(unit_added)
        self._unit_infos = dict(self._unit_infos)

        # Combat encounters
        self.player_infos: Dict[str, UnitAdded] = {unit_info.unit_id: unit_info
                                                   for unit_info in self._event_dict["UNIT_ADDED"]
                                                   if unit_info.unit_type == "PLAYER"}
        self.combat_encounters: List[BeginCombat] = []
        self._create_combat_encounters()
        for encounter in tqdm(self.combat_encounters, desc="Processing encounters", ascii=" #"):
            encounter.extract_enemies()
            encounter.process_combat_events(self)

    def __str__(self):
        return f"{self.__class__.__name__}(begin={self._begin_log.time}, end={self._end_log.time})"

    __repr__ = __str__

    def ability_info(self, ability_id) -> Optional[AbilityInfo]:
        # Stringify in case we get integers
        return self.ability_infos[str(ability_id)]

    # def ability_info_by_name(self, name: str) -> Optional[AbilityInfo]:
    #     return self._ability_infos_by_name.get(name)

    def player_info(self, unit_id) -> Optional[UnitAdded]:
        # Stringify in case we get integers
        return self.player_infos[str(unit_id)]

    def unit_info(self, unit_id: str, event_id: int) -> Optional[UnitAdded]:
        unit_added = self._unit_infos.get(unit_id)
        if unit_added is None:
            return
        # Return the event that occurred the shortest time delta before the current event
        unit_added = sorted([unit for unit in unit_added if unit.id <= event_id], key=lambda unit: event_id - unit.id)
        return unit_added[0]

    def _match_event_infos(self):
        for effect_info in self._event_dict["EFFECT_INFO"]:
            self.ability_infos[effect_info.ability_id].effect_info = effect_info

    def _create_combat_encounters(self):
        current_encounter: BeginCombat = None
        for event in self._events:
            if isinstance(event, BeginCombat):
                current_encounter = event
            elif isinstance(event, EndCombat):
                current_encounter.end_combat = event
                event.begin_combat = current_encounter
                self.combat_encounters.append(current_encounter)
                current_encounter = None
            elif isinstance(event, AbilityInfo) or isinstance(event, EffectInfo):
                continue
            elif current_encounter is not None:
                current_encounter.events.append(event)
                if isinstance(event, PlayerInfo):
                    event.update_info(self)
        assert current_encounter is None

    def _match_unit_events(self):
        """
        Unit ids of units that were removed can be reused for later units. Hence go over the events in the order they
        occurred in.
        """
        unit_events = [event for event in self._events
                       if event.event_type in ["UNIT_ADDED", "UNIT_CHANGED", "UNIT_REMOVED"]]
        added_units = {}
        for event in unit_events:
            if isinstance(event, UnitAdded):
                assert event.unit_id not in added_units, f"Duplicate unit added event with id {event.id}"
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
    def parse_log(cls, file: str, multiple: bool = False):
        path = Path(file)
        path = path.absolute()
        csv_file = read_csv(str(path), has_header=False)
        events = []
        count = 0
        logs = []
        previous_event = None
        for line in tqdm(csv_file, desc=f"Parsing log {path}", ascii=" #"):
            event = Event.create(count, int(line[0]), line[1], *line[2:])
            if previous_event is not None:
                event.previous = previous_event
            events.append(event)
            previous_event = event
            count += 1
            if isinstance(event, EndLog):
                log = cls(events)
                if multiple:
                    # We have a separate log starting after this line
                    logs.append(log)
                    events = []
                    cpunt = 0
                else:
                    return log
        return logs
