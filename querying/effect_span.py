from collections import defaultdict
from datetime import timedelta
from typing import Union, List

from logger import logger
from loading import Event, AbilityInfo, EffectChanged, UnitAdded, BeginCombat

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

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.start}, end={self.end}, ability={self.ability})"


class UptimeSpan(object):
    def __init__(self, start: Union[EffectChanged, BeginCombat], end: EffectChanged):
        self.start = start
        self.end = end
        # If the effect got applied before combat started, the start event will be the encounter itself
        if isinstance(start, EffectChanged):
            # Don't compare ability ids since we want to be able to merge effects with the same name
            assert start.ability.name == end.ability.name, f"Trying to create an effect span for different abilities ({start.ability}, {end.ability})"
            # Only the source or target unit has to be the same, since we want to merge multiple applications of effecfts of different units on a certain source or target unit
            assert start.unit_id == end.unit_id or start.target_unit_id == end.target_unit_id, f"Trying to create an effect span for different units ({start.unit_id}, {end.unit_id})"
            assert start.status == "GAINED" or start.status == "UPDATED", f"Trying to create an effect span for start ability that is not of type GAINED or UPDATED {start}"
            assert end.status == "FADED" or end.status == "UPDATED", f"Trying to create an effect span for start ability that is not of type FADED or UPDATED {end}"

    def duration(self) -> timedelta:
        return self.end.time - self.start.time

    def overlaps(self, other: 'UptimeSpan'):
        # Is this span nested in the other span or the other span nested in this span
        is_nested = (other.start.time <= self.start.time <= self.end.time <= other.end.time) or (self.start.time <= other.start.time <= other.end.time <= self.end.time)
        # Does this span start before and end during the other span
        left_overlap = self.start.time <= other.start.time <= self.end.time <= other.end.time
        # Does this span start during the other span but end after it
        right_overlap = other.start.time <= self.start.time <= other.end.time <= self.end.time
        return is_nested or left_overlap or right_overlap

    @classmethod
    def merge(cls, span: 'UptimeSpan', other_span: 'UptimeSpan') -> 'UptimeSpan':
        assert span.overlaps(other_span), f"Trying to merge non-overlapping spans {span} and {other_span}"
        start = min(span.start, other_span.start, key=lambda event: event.time)
        end = max(span.end, other_span.end, key=lambda event: event.time)
        return cls(start, end)


class PhantomUptimeSpan(UptimeSpan):
    def __init__(self, start: Union[BeginCombat, EffectChanged]):
            self.start = start
            self.end = None


class EffectUnitSpan(EffectSpan):
    def __init__(self, ability: AbilityInfo, start: Event, end: Event, source_unit: UnitAdded = None, target_unit: UnitAdded = None, uptime_spans: List[UptimeSpan] = None):
        super(EffectUnitSpan, self).__init__(ability=ability, start=start, end=end)
        self.source_unit = source_unit
        self.target_unit = target_unit

        self.uptime_spans = uptime_spans or self._uptime_spans()
        self._merge_uptime_spans()

    def _filter_event(self, event: Event):
        return super()._filter_event(event) and (self.source_unit is None or event.unit == self.source_unit) and (self.target_unit is None or event.target_unit == self.target_unit)

    def _uptime_spans(self):
        start = None
        spans = []
        phantom_spans = []
        for event in self:
            if start is None and event.status == "GAINED":
                start = event
            elif start is not None and event.status == "GAINED":
                # handle phantom span (end event never got logged)
                phantom_span = PhantomUptimeSpan(start)
                phantom_spans.append(phantom_span)
                start = event
            elif event.status == "FADED":
                if start is None:
                    start = self.start
                span = UptimeSpan(start, event)
                spans.append(span)
                start = None
            elif event.status == "UPDATED":
                # TODO: handle UPDATED status (stack count gets increase, i.e., with stagger)
                span = UptimeSpan(start, event)
                spans.append(span)
                start = event
            else:
                raise RuntimeError(f"Span computation errored on span: {self}")
        if len(phantom_spans) > 0:
            logger().warn(f"Filtered {len(phantom_spans)} phantom spans in {self}")
        return spans

    def _merge_uptime_spans(self):
        if len(self.uptime_spans) == 0:
            return
        merged_spans = [self.uptime_spans[0]]
        for span in self.uptime_spans[1:]:
            # The spans are already ordered by time so just check if current span overlaps with the last seen and merge if they do (and replace the last seen span with the updated merged span)
            if span.overlaps(merged_spans[-1]):
                merged = UptimeSpan.merge(span, merged_spans[-1])
                merged_spans[-1] = merged
                pass
            else:
                merged_spans.append(span)
        self.uptime_spans = merged_spans

    @property
    def total_debuff_time(self):
        return sum([span.duration().total_seconds() for span in self.uptime_spans])

    @property
    def relative_debuff_uptime(self):
        combat_time = self.end.time - self.start.time
        return self.total_debuff_time / combat_time.total_seconds()

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.start}, end={self.end}, ability={self.ability}, source_unit={self.source_unit} target_unit={self.target_unit})"

    @classmethod
    def merge(cls, span: 'EffectUnitSpan', other_span: 'EffectUnitSpan') -> 'EffectUnitSpan':
        assert span.ability.name == other_span.ability.name \
               and span.source_unit == other_span.source_unit \
               and span.target_unit == other_span.target_unit \
               and span.start == other_span.start \
               and span.end == other_span.end, f"Trying to merge incompatible spans {span} and {other_span}"
        # Merge the sorted lists in linear time instead of sorting the merged list as if it were unsorted
        merged_uptime_spans = []
        span_index = 0
        other_span_index = 0
        while span_index < len(span.uptime_spans) and other_span_index < len(other_span.uptime_spans):
            span_candidate = span.uptime_spans[span_index]
            other_span_candidate = other_span.uptime_spans[other_span_index]
            if span_candidate.start.time <= other_span_candidate.start.time:
                merged_uptime_spans.append(span_candidate)
                span_index += 1
            else:
                merged_uptime_spans.append(other_span_candidate)
                other_span_index += 1
        # One of the lists was fully inserted and now just append from the last list
        if span_index == len(span.uptime_spans) and other_span_index < len(other_span.uptime_spans):
            merged_uptime_spans.extend(other_span.uptime_spans[other_span_index:])
        elif span_index < len(span.uptime_spans) and other_span_index == len(other_span.uptime_spans):
            merged_uptime_spans.extend(span.uptime_spans[span_index:])

        return cls(ability=span.ability, start=span.start, end=span.end, source_unit=span.source_unit, target_unit=span.target_unit, uptime_spans=merged_uptime_spans)
