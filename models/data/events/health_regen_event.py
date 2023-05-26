from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded


class HealthRegen(Event):
    event_type: str = "HEALTH_REGEN"

    def __init__(self,
                 id: int,
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
        super(HealthRegen, self).__init__(id)
        self.unit_id = int(unit_id)
        self.effective_regen = int(effective_regen)
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
        self.z_coord = z_coord

        self.unit: UnitAdded = None