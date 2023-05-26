from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .ability_info import AbilityInfo
    from .unit_added import UnitAdded


class TargetEvent(Event):
    def __init__(self,
                 id: int,
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
        super(TargetEvent, self).__init__(id)

        # Source information
        self.unit_id = int(unit_id)
        self.ability_id = int(ability_id)

        # These values occur in the form '42384/42384'
        self.current_health, self.max_health = [int(part) for part in health.split("/")]
        self.current_magicka, self.max_magicka = [int(part) for part in magicka.split("/")]
        self.current_stamina, self.max_stamina = [int(part) for part in stamina.split("/")]
        # Occurs in the form '11/500' with 500 always being the maximum value
        self.ultimate = int(ultimate.split("/")[0])
        self.werewolf_ultimate = werewolf_ultimate
        self.shield = shield

        self.x_coord = x_coord
        self.y_coord = y_coord
        self.heading_radians = heading_radians

        # Target information (if it exists)
        if target_unit_id != "*":
            self.target_unit_id = target_unit_id
            self.target_current_health, self.target_maximum_health = [int(part) for part in target_health.split("/")]
            self.target_current_magicka, self.target_maximum_magicka = [int(part) for part in target_magicka.split("/")]
            self.target_current_stamina, self.target_maximum_stamina = [int(part) for part in target_stamina.split("/")]
            # Occurs in the form '11/500' with 500 always being the maximum value
            self.target_ultimate = int(target_ultimate.split("/")[0])
            self.target_werewolf_ultimate = target_werewolf_ultimate
            self.target_shield = target_shield

            self.target_x_coord = target_x_coord
            self.target_y_coord = target_y_coord
            self.target_heading_radians = target_heading_radians
        else:
            self.target_unit_id = None

        # Ability that was used for this event
        self.ability: AbilityInfo = None
        # Unit that cast this event
        self.unit: UnitAdded = None
        # If set, unit that was targeted by this event
        self.target_unit: UnitAdded = None

    def filter_by_type_and_target(self, event_type, target: UnitAdded):
        return isinstance(self, event_type) and self.target_unit == target
