from __future__ import annotations

from typing import TYPE_CHECKING, List

from utils import parse_epoch_time
from .event import Event

if TYPE_CHECKING:
    from .unit_events import UnitAdded


class AbilityInfo(Event):
    event_type: str = "ABILITY_INFO"

    def __init__(self, id: int, ability_id: str, name: str, icon_path: str, unknown1, unknown2):
        """
        :param unknown1: 'T' or 'F'
        :param unknown2: 'T' or 'F'
        """
        super(AbilityInfo, self).__init__(id, unknown1, unknown2)
        self.ability_id = ability_id
        self.name = name
        self.icon_path = icon_path
        self.effect_info: EffectInfo = None


class EffectInfo(Event):
    event_type: str = "EFFECT_INFO"

    def __init__(self, id: int, ability_id: str, effect_type: str, unknown1, unknown2, unknown3=None):
        """
        :param unknown1: Usually 'NONE'
        :param unknown2: 'T' or 'F'
        :param unknown3: If set some kind of id
        """
        super(EffectInfo, self).__init__(id, unknown1, unknown2, unknown3)
        self.ability_id = ability_id
        self.effect_type = effect_type


class TargetEvent(Event):
    def __init__(self,
                 id: int,
                 unknowns: List[str],
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 deprecated_ultimate: str,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_deprecated_ultimate: str = None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_z_coord: str = None):
        super(TargetEvent, self).__init__(id, *unknowns)

        # Source information
        self.unit_id = unit_id
        self.ability_id = ability_id

        # These values occur in the form '42384/42384'
        self.current_health, self.max_health = [int(part) for part in health.split("/")]
        self.current_magicka, self.max_magicka = [int(part) for part in magicka.split("/")]
        self.current_stamina, self.max_stamina = [int(part) for part in stamina.split("/")]
        # Occurs in the form '11/500' with 500 always being the maximum value
        self.ultimate = int(ultimate.split("/")[0])
        self.deprecated_ultimate = deprecated_ultimate

        self.x_coord = x_coord
        self.y_coord = y_coord
        self.z_coord = z_coord

        # Target information (if it exists)
        if target_unit_id != "*":
            self.target_unit_id = target_unit_id
            self.target_current_health, self.target_maximum_health = [int(part) for part in target_health.split("/")]
            self.target_current_magicka, self.target_maximum_magicka = [int(part) for part in target_magicka.split("/")]
            self.target_current_stamina, self.target_maximum_stamina = [int(part) for part in target_stamina.split("/")]
            # Occurs in the form '11/500' with 500 always being the maximum value
            self.target_ultimate = int(target_ultimate.split("/")[0])
            self.target_deprecated_ultimate = target_deprecated_ultimate

            self.target_x_coord = target_x_coord
            self.target_y_coord = target_y_coord
            self.target_z_coord = target_z_coord
        else:
            self.target_unit_id = None

        self.ability: AbilityInfo = None
        self.unit: UnitAdded = None
        self.target_unit: UnitAdded = None


class BeginCast(TargetEvent):
    event_type: str = "BEGIN_CAST"

    def __init__(self,
                 id: int,
                 unknown1,
                 unknown2,
                 cast_effect_id: str,
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 deprecated_ultimate: str,
                 unknown6,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_deprecated_ultimate: str = None,
                 unknown16=None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_z_coord: str = None):
        """
        :param unknown1: Some kind of integer (usually '0', sometimes '8000', '100', '25000')
        :param unknown2: 'T' or 'F'
        :param unknown6: Seems to always be '0'
        :param unknown16: Seems to always be '0'
        """
        super(BeginCast, self).__init__(id=id,
                                        unknowns=[unknown1, unknown2, unknown6, unknown16],
                                        ability_id=ability_id,
                                        unit_id=unit_id,
                                        health=health,
                                        magicka=magicka,
                                        stamina=stamina,
                                        ultimate=ultimate,
                                        deprecated_ultimate=deprecated_ultimate,
                                        x_coord=x_coord,
                                        y_coord=y_coord,
                                        z_coord=z_coord,
                                        target_unit_id=target_unit_id,
                                        target_health=target_health,
                                        target_magicka=target_magicka,
                                        target_stamina=target_stamina,
                                        target_ultimate=target_ultimate,
                                        target_deprecated_ultimate=target_deprecated_ultimate,
                                        target_x_coord=target_x_coord,
                                        target_y_coord=target_y_coord,
                                        target_z_coord=target_z_coord)

        self.cast_effect_id = cast_effect_id
        self.cancelled_end_cast: EndCast = None
        self.end_cast: EndCast = None
        self.duplicate_end_casts: List[EndCast] = []

    @property
    def completed(self):
        return self.end_cast is not None and self.cancelled_end_cast is None

    @property
    def cancelled(self):
        return self.end_cast is not None and self.cancelled_end_cast is not None


class EndCast(Event):
    event_type: str = "END_CAST"

    def __init__(self, id: int, status: str, cast_effect_id, ability_id, unknown2=None, unknown3=None):
        """
        :param unknown2: Some kind of id
        :param unknown3: Some kind of id
        """
        super(EndCast, self).__init__(id, unknown2, unknown3)
        self.ability_id = ability_id
        self.status = status
        self.cast_effect_id = cast_effect_id

        self.begin_cast: BeginCast = None


class EffectChanged(TargetEvent):
    event_type: str = "EFFECT_CHANGED"

    def __init__(self,
                 id: int,
                 status: str,
                 unknown1,
                 cast_effect_id: str,
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 deprecated_ultimate: str,
                 unknown5,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_deprecated_ultimate: str = None,
                 unknown15=None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_z_coord: str = None,
                 unknown19=None):
        """
        :param unknown1: Some kind of integer (usually '1')
        :param unknown5: Seems to always be '0'
        :param unknown15: Seems to always be '0'
        :param unknown19: Another epoch timestamp
        """
        super(EffectChanged, self).__init__(id=id,
                                            unknowns=[unknown1, unknown5, unknown15, unknown19],
                                            ability_id=ability_id,
                                            unit_id=unit_id,
                                            health=health,
                                            magicka=magicka,
                                            stamina=stamina,
                                            ultimate=ultimate,
                                            deprecated_ultimate=deprecated_ultimate,
                                            x_coord=x_coord,
                                            y_coord=y_coord,
                                            z_coord=z_coord,
                                            target_unit_id=target_unit_id,
                                            target_health=target_health,
                                            target_magicka=target_magicka,
                                            target_stamina=target_stamina,
                                            target_ultimate=target_ultimate,
                                            target_deprecated_ultimate=target_deprecated_ultimate,
                                            target_x_coord=target_x_coord,
                                            target_y_coord=target_y_coord,
                                            target_z_coord=target_z_coord)
        self.status = status
        self.cast_effect_id = cast_effect_id

        self.gained_event: TargetEvent = None
        self.faded_event: TargetEvent = None


class CombatEvent(TargetEvent):
    event_type: str = "COMBAT_EVENT"

    def __init__(self,
                 id: int,
                 type: str,
                 damage_type,
                 resource_type: str,
                 damage: str,
                 unknown2,
                 cast_effect_id: str,
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 deprecated_ultimate: str,
                 unknown6,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_deprecated_ultimate: str = None,
                 unknown16=None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_z_coord: str = None):
        """
        :param unknown2: Some kind of id/integer
        :param unknown6: Seems to always be '0'
        :param unknown16: Seems to always be '0'
        """
        super(CombatEvent, self).__init__(id=id,
                                          unknowns=[unknown2, unknown6, unknown16],
                                          ability_id=ability_id,
                                          unit_id=unit_id,
                                          health=health,
                                          magicka=magicka,
                                          stamina=stamina,
                                          ultimate=ultimate,
                                          deprecated_ultimate=deprecated_ultimate,
                                          x_coord=x_coord,
                                          y_coord=y_coord,
                                          z_coord=z_coord,
                                          target_unit_id=target_unit_id,
                                          target_health=target_health,
                                          target_magicka=target_magicka,
                                          target_stamina=target_stamina,
                                          target_ultimate=target_ultimate,
                                          target_deprecated_ultimate=target_deprecated_ultimate,
                                          target_x_coord=target_x_coord,
                                          target_y_coord=target_y_coord,
                                          target_z_coord=target_z_coord)
        # Something like 'HOT_TICK', 'HOT_TICK_CRITICAL', 'QUEUED', 'ABILITY_ON_COOLDOWN'
        self.type = type
        # Damage type for damage events, otherwise 'GENERIC' or 'INVALID'
        self.damage = int(damage)
        self.damage_type = damage_type
        # Something like 'MAGICKA', 'INVALID'
        self.resource_type = resource_type
        self.cast_effect_id = cast_effect_id


class SoulGemResurectionAcceptedEvent(CombatEvent):
    """
    Filler class for events of players accepting soul gem resurrections. The ablity id will be 0 and have no matching info event.
    """
    pass


class HealthRegen(Event):
    event_type: str = "HEALTH_REGEN"

    def __init__(self,
                 id: int,
                 unknown1,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 deprecated_ultimate: str,
                 unknown4,
                 x_coord: str,
                 y_coord: str,
                 z_coord: str):
        """
        :param unknown1: Could be amount healed
        :param unknown4: Seems to always be '0'
        """
        super(HealthRegen, self).__init__(id, unknown1, unknown4)
        self.unit_id = unit_id
        # These values occur in the form '42384/42384'
        self.current_health, self.max_health = [int(part) for part in health.split("/")]
        self.current_magicka, self.max_magicka = [int(part) for part in magicka.split("/")]
        self.current_stamina, self.max_stamina = [int(part) for part in stamina.split("/")]
        # Occurs in the form '11/500' with 500 always being the maximum value
        self.ultimate = int(ultimate.split("/")[0])
        self.deprecated_ultimate = deprecated_ultimate

        self.x_coord = x_coord
        self.y_coord = y_coord
        self.z_coord = z_coord

        self.unit: UnitAdded = None
