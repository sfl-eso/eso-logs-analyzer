from models import Event


class EventSpan(object):
    def __init__(self, start: Event, end: Event):
        self.start: Event = start
        self.end: Event = end
        self._current: Event = start

    def __iter__(self):
        return self

    def __next__(self):
        current = self._current
        while not self._filter_event(current):
            if current.order_id > self.end.order_id:
                raise StopIteration
            current = current.next

        if current.order_id > self.end.order_id:
            raise StopIteration

        self._current = current.next
        return current

    def _filter_event(self, event: Event):
        return True

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.start}, end={self.end})"

    __repr__ = __str__
