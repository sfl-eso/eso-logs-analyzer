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

    def __reversed__(self):
        event = self.end

        while event != self.start:
            yield event
            event = event.previous

        # Finish with the given target event of the span
        yield self.start

    def __eq__(self, other):
        if not isinstance(other, EventSpan):
            return False
        return self.start.id == other.start.id and self.end.id == other.end.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.start.id, self.end.id))

    def __contains__(self, item):
        if isinstance(item, Event):
            return self.start <= item <= self.end
        elif isinstance(item, EventSpan):
            return self.start <= item.start <= self.end and self.start <= item.end <= self.end
        else:
            raise NotImplementedError

    def __len__(self):
        return self.end.id - self.start.id

    def __bool__(self):
        """
        Overwrite so that this object does not become false, when the length is 0.
        """
        return True

    def overlaps(self, other: EventSpan) -> bool:
        return (other.start.id <= self.start.id <= other.end.id) \
            or (other.start.id <= self.end.id <= other.end.id)

    @property
    def duration(self) -> timedelta:
        return self.end.time - self.start.time

    def merge(self, other: EventSpan) -> EventSpan:
        if not self.overlaps(other):
            raise RuntimeError(f"Can't merge non-overlapping spans {self} and {other}")

        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return self.__class__(start, end)
