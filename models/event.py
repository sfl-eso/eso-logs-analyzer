from datetime import datetime

from utils import all_subclasses


class Event(object):
    """
    Base event class for all the different log events.
    Details for the parameters can be found on: https://esoapi.uesp.net/current/src/ingame/slashcommands/slashcommands_shared.lua.html
    """
    event_type: str = None

    def __init__(self, id: int, *args):
        self.id = id
        self.data = args
        self._time: datetime = None

        self._previous: Event = None
        self._next: Event = None
        self.order_id = None

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    def __str__(self):
        fields = [f"{field}={value}" for field, value in self.__dict__.items() if not field.startswith("_") and field != "data" and not isinstance(value, Event)]
        fields = ", ".join(fields)
        return f"{self.__class__.__name__}({fields})"

    __repr__ = __str__

    @classmethod
    def create(cls, order_id: int, id: int, event_type: str, *args):
        from .ability_events import CombatEvent, SoulGemResurectionAcceptedEvent
        for subclass in all_subclasses(cls):
            if subclass.event_type == event_type:
                instance = subclass(id, *args)
                instance.order_id = order_id

                # Hacky way to change the class of soul gem resurrection events, since they have a non-existing ability id
                if isinstance(instance, CombatEvent) and instance.ability_id == "0":
                    instance.__class__ = SoulGemResurectionAcceptedEvent

                return instance
        raise ValueError(f"No event class found for {event_type}")

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value: 'Event'):
        self._next = value
        value._previous = self

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value: 'Event'):
        self._previous = value
        value._next = self
