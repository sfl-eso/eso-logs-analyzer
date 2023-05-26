from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, List

from .enums import CastStatus
from .event import Event
from .span_event import SpanCast
from .target_event import TargetEvent

if TYPE_CHECKING:
    from .end_cast import EndCast


class BeginCast(TargetEvent, SpanCast):
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

        self.duration = timedelta(milliseconds=int(duration_in_ms))
        self.channeled = self._convert_boolean(channeled, field_name="channeled")
        self.cast_effect_id = int(cast_effect_id)

        self.end_cast: EndCast = None
        self.duplicate_end_casts: List[EndCast] = []

    @property
    def completed(self):
        return self.end_cast is not None and self.end_cast.status == CastStatus.COMPLETED

    @property
    def cancelled(self):
        return self.end_cast is not None and self.end_cast.status == CastStatus.PLAYER_CANCELLED

    @property
    def interrupted(self):
        return self.end_cast is not None and self.end_cast.status == CastStatus.INTERRUPTED

    @property
    def end_event(self) -> Event:
        return self.end_cast

    @end_event.setter
    def end_event(self, value: Event):
        self.end_cast = value
