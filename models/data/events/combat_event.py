from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import CombatEventType, ResourceType, DamageType
from .target_event import TargetEvent

if TYPE_CHECKING:
    pass


class CombatEvent(TargetEvent):
    event_type: str = "COMBAT_EVENT"

    def __init__(self,
                 id: int,
                 type: str,
                 damage_type,
                 resource_type: str,
                 damage: str,
                 overflow: str,
                 cast_effect_id: str,
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
        super(CombatEvent, self).__init__(id=id,
                                          ability_id=ability_id,
                                          unit_id=unit_id,
                                          health=health,
                                          magicka=magicka,
                                          stamina=stamina,
                                          ultimate=ultimate,
                                          werewolf_ultimate=werewolf_ultimate,
                                          shield=shield,
                                          x_coord=x_coord,
                                          y_coord=y_coord,
                                          heading_radians=heading_radians,
                                          target_unit_id=target_unit_id,
                                          target_health=target_health,
                                          target_magicka=target_magicka,
                                          target_stamina=target_stamina,
                                          target_ultimate=target_ultimate,
                                          target_werewolf_ultimate=target_werewolf_ultimate,
                                          target_shield=target_shield,
                                          target_x_coord=target_x_coord,
                                          target_y_coord=target_y_coord,
                                          target_heading_radians=target_heading_radians)
        # Something like 'HOT_TICK', 'HOT_TICK_CRITICAL', 'QUEUED', 'ABILITY_ON_COOLDOWN'
        self.type: CombatEventType = CombatEventType(type)
        # Damage type for damage events, otherwise 'GENERIC' or 'INVALID'
        self.damage = int(damage)
        self.damage_type: DamageType = DamageType(damage_type)
        self.overflow = int(overflow)
        # Something like 'MAGICKA', 'INVALID'
        self.resource_type: ResourceType = ResourceType(resource_type)
        self.cast_effect_id = int(cast_effect_id)
