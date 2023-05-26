from models import Event, AbilityInfo, EffectChanged

from .event_span import EventSpan


class DebuffSpan(EventSpan):
    def __init__(self, ability: AbilityInfo, start: Event, end: Event):
        super(DebuffSpan, self).__init__(start=start, end=end)
        self.ability: AbilityInfo = ability
        self.event_type = EffectChanged

    def _filter_event(self, event: Event):
        return isinstance(event, self.event_type) and event.ability_id == self.ability.ability_id
