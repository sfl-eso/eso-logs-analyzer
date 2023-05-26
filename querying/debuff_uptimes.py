from collections import defaultdict
from datetime import timedelta
from typing import List

from models import BeginCombat, AbilityInfo, UnitAdded, EffectChanged

from .debuff_span import DebuffSpan


class EffectSpan(object):
    def __init__(self, start: EffectChanged, end: EffectChanged):
        self.start = start
        self.end = end
        assert start.ability_id == end.ability_id, f"Trying to create an effect span for different abilities ({start.ability_id}, {end.ability_id})"
        assert start.unit_id == end.unit_id, f"Trying to create an effect span for different units ({start.unit_id}, {end.unit_id})"
        assert start.status == "GAINED", f"Trying to create an effect span for start ability that is not of type GAINED {start}"
        assert end.status == "FADED", f"Trying to create an effect span for start ability that is not of type FADED {end}"

    def duration(self) -> timedelta:
        return self.end.time - self.start.time


def debuff_for_unit(encounter: BeginCombat, ability: AbilityInfo, unit: UnitAdded) -> dict:
    debuff_span = DebuffSpan(ability, encounter, encounter.end_combat)
    events: List[EffectChanged] = [event for event in debuff_span if event.target_unit == unit]
    start = None
    spans = []
    for event in events:
        if start is None and event.status == "GAINED":
            start = event
        elif event.status == "FADED":
            span = EffectSpan(start, event)
            spans.append(span)
            start = None
        else:
            event_string = "\n".join([str(e) for e in events])
            raise RuntimeError(f"Span computation errored on events\n{event_string}")

    total_combat_time = encounter.end_combat.time - encounter.time
    total_debuff_time = sum([span.duration() for span in spans])
    units = defaultdict(int)
    for span in spans:
        units[span.start.unit_id] += span.duration()

    return {
        "ability": ability,
        "combat_time": total_combat_time,
        "debuff_time": total_debuff_time,
        "player_debuff_time": dict(units)
    }
