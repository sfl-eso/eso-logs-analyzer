from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

from .ability_events import AbilityInfo, EffectChanged
from .unit_events import PlayerInfo, UnitAdded
from .meta_events import BeginCombat


class TimeSpan(object):
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def __radd__(self, other):
        return other + self.duration

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.start}, end={self.end}, duration={self.duration})"

    __repr__ = __str__


class AbilityUptime(object):
    def __init__(self, events: List[EffectChanged], ability: AbilityInfo, encounter: BeginCombat, target: UnitAdded):
        self.events: List[EffectChanged] = events
        self.target: UnitAdded = target
        self.ability: AbilityInfo = ability
        self.encounter: BeginCombat = encounter

        self._compute_uptime()

    def _compute_uptime(self):
        for event in self.events:
            if event.status == "GAINED":
                # TODO
                pass
            elif event.status == "FADED":
                # TODO
                pass
            elif event.status == "UPDATED":
                # TODO
                pass

    @classmethod
    def create_for_encounter(cls, ability: AbilityInfo, encounter: BeginCombat) -> List['AbilityUptime']:
        enemies = encounter.extract_enemies()
        events = [event for event in encounter.events
                  if isinstance(event, EffectChanged) and event.ability == ability and event.target_unit in enemies]
        enemy_events: Dict[UnitAdded, List[EffectChanged]] = defaultdict(list)
        for event in events:
            enemy_events[event.target_unit].append(event)

        uptimes = []
        for enemy in enemies:
            uptime = cls(events=enemy_events[enemy], ability=ability, encounter=encounter, target=enemy)
            uptimes.append(uptime)
        return uptimes

