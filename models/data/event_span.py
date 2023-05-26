from __future__ import annotations

from datetime import timedelta

from .events import Event
from ..base import Base


class EventSpan(Base):
    def __init__(self, start: Event, end: Event):
        super().__init__()
        # The start event is always the one that appeared first
        self.start = min(start, end, key=Event.sort_key)
        self.end = max(start, end, key=Event.sort_key)

    def __iter__(self):
        event = self.start

        while event != self.end:
            yield event
            event = event.next

        # Finish with the given target event of the span
        yield self.end

    def __eq__(self, other):
        return self.start.order_id == other.start.order_id and self.end.order_id == other.end.order_id

    def __hash__(self):
        return hash(f"{self.start.order_id} to {self.end.order_id}")

    def overlaps(self, other: EventSpan) -> bool:
        return (other.start.order_id <= self.start.order_id <= other.end.order_id) \
            or (other.start.order_id <= self.end.order_id <= other.end.order_id)

    @property
    def duration(self) -> timedelta:
        return self.end.time - self.start.time

    def merge(self, other: EventSpan) -> EventSpan:
        if not self.overlaps(other):
            raise RuntimeError(f"Can't merge non-overlapping spans {self} and {other}")

        start = min(self.start, other.start, key=Event.sort_key)
        end = max(self.end, other.end, key=Event.sort_key)
        return self.__class__(start, end)
