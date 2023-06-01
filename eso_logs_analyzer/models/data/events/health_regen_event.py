from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded
    from ..encounter_log import EncounterLog


class HealthRegen(Event):
    event_type: str = "HEALTH_REGEN"

    def __init__(self,
                 id: int,
                 encounter_log: EncounterLog,
                 event_id: int,
                 effective_regen: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 werewolf_ultimate: str,
                 shield: str,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str):
        super(HealthRegen, self).__init__(id, encounter_log, event_id)
        self.unit_id = int(unit_id)
        self.effective_regen = int(effective_regen)
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
        self.z_coord = z_coord

        self.unit: UnitAdded = None
