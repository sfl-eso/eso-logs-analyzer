from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from ..event_span import EventSpan


class SpanCast(Event):
    def __init__(self, *args, **kwargs):
        super(SpanCast, self).__init__(*args, **kwargs)

    @property
    def span_to_end(self) -> EventSpan:
        """
        Returns span to end event of this event. If this event does not have an end event, just return a span of this event.
        """
        from ..event_span import EventSpan
        if self.end_event is None:
            self.logger.error(f"Can't create span to unset end element for {self}")
            return super().span_to_end()

        return EventSpan(self, self.end_event)

    @property
    def end_event(self) -> Event:
        raise NotImplementedError

    @end_event.setter
    def end_event(self, value: Event):
        raise NotImplementedError
