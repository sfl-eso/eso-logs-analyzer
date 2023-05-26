from __future__ import annotations

from typing import TYPE_CHECKING, List

from .event import Event

if TYPE_CHECKING:
    from .log import EncounterLog
    from .ability_events import AbilityInfo, TargetEvent, HealthRegen


class PlayerInfo(Event):
    event_type: str = "PLAYER_INFO"

    def __init__(self, id: int, unit_id: str, *args):
        """
        :param unknown: Some kind of integer
        :param args: Information about the player split badly by the csv parser
        """
        super(PlayerInfo, self).__init__(id)
        self.unit_id = unit_id
        parsed_data = self._parse_info(",".join(args))
        self._raw_passives = parsed_data[0]
        self._raw_passives_active = parsed_data[1]
        self._raw_gear = parsed_data[2]
        self._raw_front_bar = parsed_data[3]
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
                 unit_id,
                 unit_type,
                 unknown2,
                 unknown3,
                 unknown4,
                 unknown5,
                 unknown6,
                 unknown7,
                 name: str,
                 account: str,
                 unknown8,
                 level: str,
                 champion_level: str,
                 unknown9,
                 hostility: str,
                 unknown10):
        """
        :param unknown2: 'T' or 'F'
        :param unknown3: Incrementing integer for PLAYER, '0' for others
        :param unknown4: Some kind of id for MONSTER, '0' for others
        :param unknown5: 'T' or 'F'
        :param unknown6: Some kind of id for PLAYER, '0' for others
        :param unknown7: Some kind of id for PLAYER, '0' for others
        :param unknown8: Some kind of id for PLAYER, '' for others
        :param unknown9: Some kind of id for MONSTER, '0' for others
        :param unknown10: 'T' or 'F'
        """
        super(UnitAdded, self).__init__(id, unknown2, unknown3, unknown4, unknown5, unknown6, unknown7, unknown8,
                                        unknown9, unknown10)
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.name = name
        self.account = account
        self.level = level
        self.champion_level = champion_level
        self.hostility = hostility

        self.unit_changed: List[UnitChanged] = []
        self.unit_removed: UnitRemoved = None

        self.combat_events_source: List[TargetEvent] = []
        self.combat_events_target: List[TargetEvent] = []
        self.health_regen_events: List[HealthRegen] = []

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, unit_type={self.unit_type}, " \
               f"name={self.name}, account={self.account}, level={self.level}, champion_level={self.champion_level}, " \
               f"hostility={self.hostility}, unit_changed={len(self.unit_changed)}, " \
               f"unit_removed={self.unit_removed is not None})"

    __repr__ = __str__


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
                 unknown2,
                 unknown3,
                 name: str,
                 account: str,
                 unknown4,
                 level: str,
                 champion_level: str,
                 unknown5,
                 hostility: str,
                 unknown6):
        """
        :param unknown2: Some kind of id for PLAYER, '0' for others
        :param unknown3: Some kind of id for PLAYER, '0' for others
        :param unknown4: Some kind of id for PLAYER, '0' for others
        :param unknown5: Often '0'
        :param unknown6: 'T' or 'F'
        """
        super(UnitChanged, self).__init__(id, unknown2, unknown3, unknown4, unknown5, unknown6)
        self.unit_id = unit_id
        self.name = name
        self.account = account
        self.level = int(level)
        self.champion_level = int(champion_level)
        self.hostility = hostility

        self.unit_added: UnitAdded = None

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, name={self.name}, " \
               f"account={self.account}, level={self.level}, champion_level={self.champion_level}, " \
               f"hostility={self.hostility}, unit_added={self.unit_added is not None})"

    __repr__ = __str__
