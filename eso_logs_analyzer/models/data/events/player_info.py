from __future__ import annotations

from typing import TYPE_CHECKING, List

from .event import Event

if TYPE_CHECKING:
    from .ability_info import AbilityInfo
    from .unit_added import UnitAdded
    from ..encounter_log import EncounterLog


class PlayerInfo(Event):
    event_type: str = "PLAYER_INFO"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, unit_id: str, *args):
        """
        :param args: Information about the player split badly by the csv parser
        """
        super(PlayerInfo, self).__init__(id, encounter_log, event_id)
        self.unit_id = int(unit_id)
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

    def resolve_ability_and_effect_info_references(self, encounter_log: EncounterLog):
        """
        Store the player unit objects in addition to the ability infos.
        """
        self.unit = encounter_log.player_unit_added[self.unit_id]
        self.passives = [encounter_log.ability_infos[int(ability)] for ability in self._raw_passives if ability]
        self.front_bar = [encounter_log.ability_infos[int(ability)] for ability in self._raw_front_bar if ability]
        self.back_bar = [encounter_log.ability_infos[int(ability)] for ability in self._raw_back_bar if ability]
