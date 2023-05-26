from __future__ import annotations

from datetime import timedelta

from .events import Event
from ..base import Base


class EventSpan(Base):
    def __init__(self, start: Event, end: Event):
        super().__init__()
        # The start event is always the one that appeared first
        self.start = min(start, end)
        self.end = max(start, end)

    def __iter__(self):
        event = self.start

        while event != self.end:
            yield event
            event = event.next

        # Finish with the given target event of the span
        yield self.end

    def __eq__(self, other):
        if not isinstance(other, EventSpan):
            return False
        return self.start.order_id == other.start.order_id and self.end.order_id == other.end.order_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.start.order_id, self.end.order_id))

    def __contains__(self, item):
        if isinstance(item, Event):
            return self.start <= item <= self.end
        elif isinstance(item, EventSpan):
            return self.start <= item.start <= self.end and self.start <= item.end <= self.end
        else:
            raise NotImplementedError

    def overlaps(self, other: EventSpan) -> bool:
        return (other.start.order_id <= self.start.order_id <= other.end.order_id) \
            or (other.start.order_id <= self.end.order_id <= other.end.order_id)

    @property
    def duration(self) -> timedelta:
        return self.end.time - self.start.time

    def merge(self, other: EventSpan) -> EventSpan:
        if not self.overlaps(other):
            raise RuntimeError(f"Can't merge non-overlapping spans {self} and {other}")

        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return self.__class__(start, end)
