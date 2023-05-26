from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple

from tqdm import tqdm

from loading import Event, AbilityInfo, BeginLog, EndLog, BeginCombat, EndCombat, EffectInfo, PlayerInfo, UnitAdded, \
    UnitRemoved, UnitChanged, TrialInit, TargetEvent, SoulGemResurectionAcceptedEvent, BeginCast, EndCast
from logger import logger
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

        # Ability Infos
        self.ability_infos: Dict[str, AbilityInfo] = {ability_info.ability_id: ability_info
                                                      for ability_info in self._event_dict["ABILITY_INFO"]}
        self._match_event_infos()
        self.create_metadata()

        # Unit spawns and kills
        self._match_unit_events()
        # self._unit_infos: Dict[tuple, List[UnitAdded]] = defaultdict(list)
        # for unit_added in self._event_dict["UNIT_ADDED"]:
        #     self._unit_infos[(unit_added.id, unit_added.unit_id)].append(unit_added)
        # self._unit_infos = dict(self._unit_infos)

        # Combat encounters
        self.player_infos: Dict[str, UnitAdded] = {unit_info.unit_id: unit_info
                                                   for unit_info in self._event_dict["UNIT_ADDED"]
                                                   if unit_info.unit_type == "PLAYER"}
        self.combat_encounters: List[BeginCombat] = []
        self._create_combat_encounters()
        for encounter in tqdm(self.combat_encounters, desc="Initializing encounters"):
            # First check that we won't get unit id collisions in this encounter
            encounter.check_unit_overlap()
            # Extract all hostile units that are active during this encounter
            encounter.extract_hostile_units()

        self._merge_combat_encounters()

        for encounter in tqdm(self.combat_encounters, desc="Processing encounters"):
            encounter.process_combat_events()

    def __str__(self):
        return f"{self.__class__.__name__}(begin={self._begin_log.time}, end={self._end_log.time})"

    __repr__ = __str__

    def create_metadata(self):
        # The cache will be used to confirm that every cast was ended, and the dict is just needed for lookups of duplicate end cast events
        begin_cast_cache: Dict[str, BeginCast] = {}
        begin_cast_dict: Dict[str, BeginCast] = {}

        for event in tqdm(self._events, desc="Creating event metadata"):
            # Set the epoch time for each event by computing the diff to the begin log event
            if not isinstance(event, TrialInit):
                event.time = self._begin_log.event_time(event.id)

            # Set ability field for every event that has a ability id
            if hasattr(event, "ability_id") and not isinstance(event,
                                                               SoulGemResurectionAcceptedEvent) and not isinstance(
                event, AbilityInfo):
                event.ability = self.ability_info(event.ability_id)

            # Match begin cast and end cast events
            if isinstance(event, BeginCast):
                begin_cast_cache[event.cast_effect_id] = event
                begin_cast_dict[event.cast_effect_id] = event
            elif isinstance(event, EndCast):
                try:
                    begin_event = begin_cast_dict[event.cast_effect_id]
                except KeyError as e:
                    logger().warn(f"No begin cast for end cast {event}")
                    continue
                event.begin_cast = begin_event
                if event.status == "COMPLETED" and begin_event.end_cast is not None:
                    begin_event.duplicate_end_casts.append(event)
                elif event.status == "COMPLETED":
                    begin_event.end_cast = event
                    del begin_cast_cache[event.cast_effect_id]
                elif event.status == "PLAYER_CANCELLED" or event.status == "INTERRUPTED":
                    begin_event.cancelled_end_cast = event
                else:
                    logger().error(f"Found EndCast event with unknown status {event.status}: {event} ")
        if len(begin_cast_cache) > 0:
            logger().warn(f"Found {len(begin_cast_cache)} begin events without end")

    def ability_info(self, ability_id) -> Optional[AbilityInfo]:
        # Stringify in case we get integers
        return self.ability_infos[str(ability_id)]

    # def ability_info_by_name(self, name: str) -> Optional[AbilityInfo]:
    #     return self._ability_infos_by_name.get(name)

    def player_info(self, unit_id) -> Optional[UnitAdded]:
        # Stringify in case we get integers
        return self.player_infos[str(unit_id)]

    # def unit_info(self, unit_id: str, event_id: int) -> UnitAdded:
    #     return self._unit_infos[(event_id, unit_id)]

    def _match_event_infos(self):
        for effect_info in self._event_dict["EFFECT_INFO"]:
            self.ability_infos[effect_info.ability_id].effect_info = effect_info

    def _create_combat_encounters(self):
        current_encounter: BeginCombat = None
        # Track units that are alive at the beginning and end of an encounter
        unit_pool: Dict[str, UnitAdded] = {}
        # Track units that occur as actors during an encounter (i.e., they may spawn and die in the same encounter)
        active_units = []
        for event in self._events:
            # Skip info events since they are queried separately
            if isinstance(event, AbilityInfo) or isinstance(event, EffectInfo):
                continue

            # Track active units so encounters contain units spawned before combat started
            if isinstance(event, UnitAdded):
                unit_pool[event.unit_id] = event
                # Track this unit for this encounter even if it dies before the encounter ends
                active_units.append(event)
            elif isinstance(event, UnitRemoved):
                del unit_pool[event.unit_id]

            # Track encounter start and end and add any other event to the combat span
            if isinstance(event, BeginCombat):
                current_encounter = event
                current_encounter.start_units = list(unit_pool.values())
                # Reset the active units to the units that are alive as the encounter starts
                active_units = current_encounter.start_units
            elif isinstance(event, EndCombat):
                current_encounter.end_combat = event
                current_encounter.end_units = list(unit_pool.values())

                # Save the active units and reset the count for the next event
                current_encounter.active_units = active_units
                active_units = []

                # Mark the end encounter event for the current encounter
                event.begin_combat = current_encounter
                self.combat_encounters.append(current_encounter)
                current_encounter = None
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

    def _merge_combat_encounters(self):
        UNIT_ID = "UNIT_ID"
        MIN_HP = "MIN_HP"
        MAX_HP = "MAX_HP"

        # Contains encounters that are candidates for merging and the metadata for bosses in those encounters
        past_encounters: List[Tuple[BeginCombat, Dict[Tuple[str, str], dict]]] = []
        merged_encounters = []
        # Create encounter pairing
        for encounter in self.combat_encounters:
            # We only merge boss encounters
            if not encounter.is_boss_encounter:
                merged_encounters.append([encounter])
                continue

            # This is the first boss encounter
            if not past_encounters:
                past_encounters.append((encounter, {}))
                continue

            # Test if the boss units have the same unit ids
            # Test if encounters should be merged by comparing unit ids and current HP. Only compare units if they
            # share the unit id and if the HP is monotonically decreasing throughout the encounters.
            boss_units = {}
            for boss in encounter.boss_units:
                target_events = [event for event in encounter.events
                                 if isinstance(event, TargetEvent) and event.target_unit_id == boss.unit_id]
                if not target_events:
                    # Ignore bosses that have not been subject to target events. These may be units added due to
                    # hard mode mechanics, that do not directly interact with the players.
                    continue
                min_hp_in_encounter = min(event.target_current_health for event in target_events)
                max_hp_in_encounter = max(event.target_current_health for event in target_events)
                boss_units[(boss.name, boss.unit_id)] = {UNIT_ID: boss.unit_id, MIN_HP: min_hp_in_encounter,
                                                         MAX_HP: max_hp_in_encounter}

            same_units = False
            for past_encounter, past_encounter_boss_metadata in past_encounters:
                for boss_name, boss_unit_id in past_encounter_boss_metadata:
                    if (boss_name, boss_unit_id) not in boss_units:
                        # The combination of unit name and unit id are not the same as in the previous encounter. These
                        # encounters should not be merged.
                        continue
                    past_encounter_metadata = past_encounter_boss_metadata[(boss_name, boss_unit_id)]
                    current_metadata = boss_units[(boss_name, boss_unit_id)]

                    # The encounters should be merged if the minimum HP during the last encounter is higher or equal to
                    # the maximum HP of the matching unit between the two encounters. This means that the HP is
                    # monotonically decreasing. If the encounters were separate encounters, the max HP in the second
                    # encounter would be at 100% current HP and thus always higher than the minimum HP of the first
                    # encounter.
                    same_units = same_units or past_encounter_metadata[MIN_HP] >= current_metadata[MAX_HP]

            # This encounter shares a boss unit with past encounters
            if same_units:
                past_encounters.append((encounter, boss_units))
            else:
                # This encounter does not share a boss unit with past encounters. Hence, we have nothing to merge with past encounters anymore
                merged_encounters.append([encounter[0] for encounter in past_encounters])
                past_encounters = [(encounter, boss_units)]
        # Add the last set of encounters
        if past_encounters:
            merged_encounters.append([encounter[0] for encounter in past_encounters])

        self.combat_encounters = sorted(
            [BeginCombat.merge_encounters(encounter_match) for encounter_match in merged_encounters],
            key=lambda e: e.time)

    @classmethod
    def parse_log(cls, file: Union[str, Path], multiple: bool = False):
        path = Path(file)
        path = path.absolute()
        csv_file = read_csv(str(path), has_header=False)
        events = []
        count = 0
        logs = []
        previous_event = None

        for line in tqdm(csv_file, desc=f"Parsing log {path}"):
            event = Event.create(count, int(line[0]), line[1], *line[2:])
            if previous_event is not None:
                event.previous = previous_event
            events.append(event)
            previous_event = event
            count += 1
            if isinstance(event, EndLog):
                logs.append(events)
                if multiple:
                    # We have a separate log starting after this line
                    events = []
                    count = 0
                    previous_event = None
                else:
                    break;

        logs = [cls(events) for events in logs]
        return logs if multiple else logs[0]
