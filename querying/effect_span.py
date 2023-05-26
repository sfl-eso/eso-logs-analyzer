from collections import defaultdict
from datetime import timedelta
from typing import Union

from models import Event, AbilityInfo, EffectChanged, UnitAdded, BeginCombat

from .event_span import EventSpan


class EffectSpan(EventSpan):
    def __init__(self, ability: AbilityInfo, start: Event, end: Event):
        super(EffectSpan, self).__init__(start=start, end=end)
        self.ability: AbilityInfo = ability
        self.event_type = EffectChanged

    def _filter_event(self, event: Event):
        return isinstance(event, self.event_type) and event.ability_id == self.ability.ability_id

    def debuff_by_units(self):
        units = defaultdict(list)
        for event in self:
            units[event.target_unit].append(event)
        return units


class UptimeSpan(object):
    def __init__(self, start: Union[EffectChanged, BeginCombat], end: EffectChanged):
        self.start = start
        self.end = end
        # If the effect got applied before combat started, the start event will be the encounter itself
        if isinstance(start, EffectChanged):
            assert start.ability_id == end.ability_id, f"Trying to create an effect span for different abilities ({start.ability_id}, {end.ability_id})"
            assert start.unit_id == end.unit_id, f"Trying to create an effect span for different units ({start.unit_id}, {end.unit_id})"
            assert start.status == "GAINED", f"Trying to create an effect span for start ability that is not of type GAINED {start}"
            assert end.status == "FADED", f"Trying to create an effect span for start ability that is not of type FADED {end}"

    def duration(self) -> timedelta:
        return self.end.time - self.start.time


class EffectUnitSpan(EffectSpan):
    def __init__(self, ability: AbilityInfo, start: Event, end: Event, source_unit: UnitAdded = None, target_unit: UnitAdded = None):
        super(EffectUnitSpan, self).__init__(ability=ability, start=start, end=end)
        self.source_unit = source_unit
        self.target_unit = target_unit

    def _filter_event(self, event: Event):
        return super()._filter_event(event) and (self.source_unit is None or event.unit == self.source_unit) and (self.target_unit is None or event.target_unit == self.target_unit)

    def _uptime_spans(self):
        start = None
        spans = []
        for event in self:
            if start is None and event.status == "GAINED":
                start = event
            elif event.status == "FADED":
                if start is None:
                    start = self.start
                span = UptimeSpan(start, event)
                spans.append(span)
                start = None
            else:
                raise RuntimeError(f"Span computation errored on span: {self}")
        return spans
