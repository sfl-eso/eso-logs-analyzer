from __future__ import annotations

from typing import TYPE_CHECKING

from .abstract_ability import AbstractAbility
from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded
    from ..encounter_log import EncounterLog


class TargetEvent(Event, AbstractAbility):
    def __init__(self,
                 id: int,
                 encounter_log: EncounterLog,
                 event_id: int,
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 werewolf_ultimate: str,
                 shield: str,
                 x_coord: str,
                 y_coord: str,
                 heading_radians: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_werewolf_ultimate: str = None,
                 target_shield: str = None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_heading_radians: str = None):
        super(TargetEvent, self).__init__(id, encounter_log, event_id)

        # Source information
        self.unit_id = int(unit_id)
        self.ability_id = int(ability_id)

        # These values occur in the form '42384/42384'
        self.current_health, self.max_health = self._convert_resource(health)
        self.current_magicka, self.max_magicka = self._convert_resource(magicka)
        self.current_stamina, self.max_stamina = self._convert_resource(stamina)
        # Occurs in the form '11/500' with 500 always being the maximum value
        self.ultimate, self.max_ultimate = self._convert_resource(ultimate)
        self.werewolf_ultimate = werewolf_ultimate
        self.shield = shield

        self.x_coord = x_coord
        self.y_coord = y_coord
        self.heading_radians = heading_radians

        # Target information (if it exists)
        if target_unit_id != "*":
            self.target_unit_id = int(target_unit_id)
            self.target_current_health, self.target_maximum_health = self._convert_resource(target_health)
            self.target_current_magicka, self.target_maximum_magicka = self._convert_resource(target_magicka)
            self.target_current_stamina, self.target_maximum_stamina = self._convert_resource(target_stamina)
            # Occurs in the form '11/500' with 500 always being the maximum value
            self.target_ultimate, self.target_max_ultimate = self._convert_resource(target_ultimate)
            self.target_werewolf_ultimate = target_werewolf_ultimate
            self.target_shield = target_shield

            self.target_x_coord = target_x_coord
            self.target_y_coord = target_y_coord
            self.target_heading_radians = target_heading_radians
        else:
            self.target_unit_id = None

        # Unit that cast this event
        self.unit: UnitAdded = None
        # If set, unit that was targeted by this event
        self.target_unit: UnitAdded = None

    def filter_by_type_and_target(self, event_type, target: UnitAdded):
        return isinstance(self, event_type) and self.target_unit == target
