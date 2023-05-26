from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict

from .event import Event

if TYPE_CHECKING:
    from .log import EncounterLog
    from .ability_events import AbilityInfo, TargetEvent, HealthRegen
    from .meta_events import BeginCombat


class PlayerInfo(Event):
    event_type: str = "PLAYER_INFO"

    def __init__(self, id: int, unit_id: str, *args):
        """
        :param args: Information about the player split badly by the csv parser
        """
        super(PlayerInfo, self).__init__(id)
        self.unit_id = unit_id
        parsed_data = self._parse_info(",".join(args))
        # Long term effect ability ids
        self._raw_passives = parsed_data[0]
        # Long term effect stack counts
        self._raw_passives_active = parsed_data[1]
        # Equipment info
        # <equipmentInfo> refers to the following fields for a piece of equipment: slot, id, isCP, level, trait, displayQuality, setId, enchantType, isEnchantCP, enchantLevel, enchantQuality.
        self._raw_gear = parsed_data[2]
        # Primary ability ids
        self._raw_front_bar = parsed_data[3]
        # Backup ability ids
        self._raw_back_bar = parsed_data[4]

        self.unit: UnitAdded = None
        self.passives: List[AbilityInfo] = []
        self.passives_active: List[bool] = [bool(int(active)) for active in self._raw_passives_active]
        self.front_bar: List[AbilityInfo] = []
        self.back_bar: List[AbilityInfo] = []

    def _parse_info(self, raw_data: str):
        def parse_brackets(input_str: str):
            parsed_lists = []
            current_list = ""
            num_open_brackets = 0
            for char in [str(c) for c in input_str]:
                if char == "," and num_open_brackets == 0:
                    continue
                elif char == "[":
                    current_list += char
                    num_open_brackets += 1
                elif char == "]":
                    num_open_brackets -= 1
                    current_list += char
                    if num_open_brackets == 0:
                        parsed_lists.append(current_list)
                        current_list = ""
                else:
                    current_list += char
            return parsed_lists

        merged_info = parse_brackets(raw_data)
        passives = merged_info[0][1:-1].split(",")
        passives_active = merged_info[1][1:-1].split(",")
        gear = parse_brackets(merged_info[2][1:-1])
        gear = [item[1:-1].split(",") for item in gear]
        front_bar = merged_info[3][1:-1].split(",")
        back_bar = merged_info[4][1:-1].split(",")
        return passives, passives_active, gear, front_bar, back_bar

    def update_info(self, log: EncounterLog):
        self.unit = log.player_info(self.unit_id)
        self.passives = [log.ability_info(ability) for ability in self._raw_passives if ability]
        self.front_bar = [log.ability_info(ability) for ability in self._raw_front_bar if ability]
        self.back_bar = [log.ability_info(ability) for ability in self._raw_back_bar if ability]


class UnitAdded(Event):
    event_type: str = "UNIT_ADDED"

    def __init__(self,
                 id: int,
                 unit_id: str,
                 unit_type: str,
                 is_local_player: str,
                 player_per_session_id: str,
                 monster_id: str,
                 is_boss: str,
                 class_id: str,
                 race_id: str,
                 name: str,
                 account: str,
                 character_id: str,
                 level: str,
                 champion_level: str,
                 owner_unit_id: str,
                 hostility: str,
                 is_grouped_with_local_player: str):
        super(UnitAdded, self).__init__(id)
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.name = name
        self.account = account
        self.level = level
        self.champion_level = champion_level
        self.hostility = hostility

        self.is_local_player = is_local_player == "T"
        self.player_per_session_id = player_per_session_id
        self.monster_id = monster_id
        self.is_boss = is_boss == "T"
        self.class_id = class_id
        self.race_id = race_id
        self.character_id = character_id
        self.owner_unit_id = owner_unit_id
        self.is_grouped_with_local_player = is_grouped_with_local_player == "T"

        self.unit_changed: List[UnitChanged] = []
        self.unit_removed: UnitRemoved = None

        self.combat_events_source: Dict[BeginCombat, List[TargetEvent]] = defaultdict(list)
        self.combat_events_target: Dict[BeginCombat, List[TargetEvent]] = defaultdict(list)
        self.health_regen_events: Dict[BeginCombat, List[HealthRegen]] = defaultdict(list)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, unit_type={self.unit_type}, " \
               f"name={self.name}, account={self.account}, level={self.level}, champion_level={self.champion_level}, " \
               f"hostility={self.hostility}, unit_changed={len(self.unit_changed)}, " \
               f"unit_removed={self.unit_removed is not None})"

    __repr__ = __str__

    def damage_done(self, encounter: BeginCombat, unit: UnitAdded):
        from .ability_events import CombatEvent
        damage_events: List[CombatEvent] = [event for event in self.combat_events_source[encounter] if isinstance(event, CombatEvent) and event.target_unit == unit]
        damage_done = 0
        damage_done_by_type = defaultdict(int)
        damage_done_by_ability = defaultdict(int)
        for event in damage_events:
            damage_done += event.damage
            damage_done_by_ability[event.ability] += event.damage
            damage_done_by_type[event.damage_type] += event.damage
        duration = encounter.end_combat.time - encounter.time
        dps = damage_done / duration.total_seconds()
        dps_by_type = {damage_type: damage / duration.total_seconds() for damage_type, damage in damage_done_by_type.items()}
        dps_by_ability = {ability: damage / duration.total_seconds() for ability, damage in damage_done_by_ability.items()}
        return {
            "dps": dps,
            "damage_done": damage_done,
            "dps_by_type": dps_by_type,
            "damage_by_type": damage_done_by_type,
            "dps_by_ability": dps_by_ability,
            "damage_by_ability": damage_done_by_ability,
            "duration": duration
        }

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


class UnitRemoved(Event):
    event_type: str = "UNIT_REMOVED"

    def __init__(self, id: int, unit_id: str):
        super(UnitRemoved, self).__init__(id)
        self.unit_id = unit_id
        self.unit_added: UnitAdded = None

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, " \
               f"unit_added={self.unit_added is not None})"

    __repr__ = __str__


class UnitChanged(Event):
    event_type: str = "UNIT_CHANGED"

    def __init__(self,
                 id: int,
                 unit_id: str,
                 class_id: str,
                 race_id: str,
                 name: str,
                 account: str,
                 character_id: str,
                 level: str,
                 champion_level: str,
                 owner_unit_id: str,
                 hostility: str,
                 is_grouped_with_local_player: str):
        super(UnitChanged, self).__init__(id)
        self.unit_id = unit_id
        self.name = name
        self.account = account
        self.level = int(level)
        self.champion_level = int(champion_level)
        self.hostility = hostility

        self.class_id = class_id
        self.race_id = race_id
        self.character_id = character_id
        self.owner_unit_id = owner_unit_id
        self.is_grouped_with_local_player = is_grouped_with_local_player == "T"

        self.unit_added: UnitAdded = None

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, name={self.name}, " \
               f"account={self.account}, level={self.level}, champion_level={self.champion_level}, " \
               f"hostility={self.hostility}, unit_added={self.unit_added is not None})"

    __repr__ = __str__
