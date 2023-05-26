from __future__ import annotations

from typing import TYPE_CHECKING, List

from utils import parse_epoch_time
from .event import Event

if TYPE_CHECKING:
    from .unit_events import UnitAdded


class AbilityInfo(Event):
    event_type: str = "ABILITY_INFO"

    def __init__(self, id: int, ability_id: str, name: str, icon_path: str, interruptible: str, blockable: str):
        super(AbilityInfo, self).__init__(id)
        self.ability_id = ability_id
        self.name = name
        self.icon_path = icon_path
        self.interruptible = interruptible == "T"
        self.blockable = blockable == "T"
        self.effect_info: EffectInfo = None


class EffectInfo(Event):
    event_type: str = "EFFECT_INFO"

    def __init__(self, id: int, ability_id: str, effect_type: str, status_effect_type: str, no_effect_bar: str, grants_synergy_ability_id: str = None):
        super(EffectInfo, self).__init__(id)
        self.ability_id = ability_id
        self.effect_type = effect_type
        self.status_effect_type = status_effect_type
        self.no_effect_bar = no_effect_bar == "T"
        self.grants_synergy_ability_id = grants_synergy_ability_id


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
        self.unit_id = unit_id
        self.ability_id = ability_id

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

        self.ability: AbilityInfo = None
        self.unit: UnitAdded = None
        self.target_unit: UnitAdded = None


class BeginCast(TargetEvent):
    event_type: str = "BEGIN_CAST"

    def __init__(self,
                 id: int,
                 duration_in_ms: str,
                 channeled: str,
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
        super(BeginCast, self).__init__(id=id,
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

        self.duration_in_ms = int(duration_in_ms)
        self.channeled = channeled == "T"
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

    def __init__(self, id: int, status: str, cast_effect_id, ability_id, interrupting_ability_id: str = None, interrupting_unit_id: str = None):
        super(EndCast, self).__init__(id)
        self.ability_id = ability_id
        self.status = status
        self.cast_effect_id = cast_effect_id
        self.interrupting_ability_id = interrupting_ability_id
        self.interrupting_unit_id = interrupting_unit_id

        self.begin_cast: BeginCast = None


class EffectChanged(TargetEvent):
    event_type: str = "EFFECT_CHANGED"

    def __init__(self,
                 id: int,
                 status: str,
                 stack_count: str,
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
                 target_heading_radians: str = None,
                 player_initiated_remove_cast_track_id: str = None):
        super(EffectChanged, self).__init__(id=id,
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
        self.status = status
        self.stack_count = stack_count
        self.cast_effect_id = cast_effect_id
        self.player_initiated_remove_cast_track_id = player_initiated_remove_cast_track_id

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
        self.type = type
        # Damage type for damage events, otherwise 'GENERIC' or 'INVALID'
        self.damage = int(damage)
        self.damage_type = damage_type
        self.overflow = overflow
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
        self.unit_id = unit_id
        self.effective_regen = effective_regen
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
