from __future__ import annotations

from datetime import datetime, timedelta
from typing import Type, Dict, TYPE_CHECKING, Generator

from utils import all_subclasses
from .enums import BooleanType
from ...base import Base

if TYPE_CHECKING:
    from ..encounter_log import EncounterLog


class Event(Base):
    """
    Base event class for all the different log events.
    Details for the parameters can be found on: https://esoapi.uesp.net/current/src/ingame/slashcommands/slashcommands_shared.lua.html
    """
    event_type: str = None
    subclass_for_event_type: Dict[str, Type[Event]] = None

    def __init__(self, id: int, *args):
        super().__init__()

        # Consecutive id of the event. Is a millisecond offset to the timestamp of the BEGIN_LOG event.
        self.id = id
        # Contains data fields that have not been parsed into named fields
        self.data = args

        # Time of the event. Computed by
        self._time: datetime = None

        # TODO: parent event
        # Previous event in order
        self._previous: Event = None
        # Next event in order
        self._next: Event = None
        # Line number in the source log file
        self.order_id = None

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    def __str__(self):
        fields = [f"{field}={value}" for field, value in self.__dict__.items() if
                  not field.startswith("_") and field != "data" and not isinstance(value, Event)]
        fields = ", ".join(fields)
        return f"{self.__class__.__name__}({fields})"

    __repr__ = __str__

    @classmethod
    def create(cls, order_id: int, id: int, event_type: str, *args):
        if cls.subclass_for_event_type is None:
            cls.subclass_for_event_type = {subclass.event_type: subclass for subclass in all_subclasses(cls)}

        from .combat_event import CombatEvent
        from .soul_gem_event import SoulGemResurrectionAcceptedEvent
        if event_type not in cls.subclass_for_event_type:
            raise ValueError(f"No event class found for {event_type}")

        subclass = cls.subclass_for_event_type[event_type]
        instance = subclass(id, *args)
        instance.order_id = order_id

        # Hacky way to change the class of soul gem resurrection events, since they have a non-existing ability id
        if isinstance(instance, CombatEvent) and instance.ability_id == "0":
            instance.__class__ = SoulGemResurrectionAcceptedEvent

        return instance

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value: Event):
        self._next = value
        value._previous = self

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value: Event):
        self._previous = value
        value._next = self

    # TODO: proper span class with __iter__ method and functions to check if an event is in the span and if spans overlap (and to merge them)
    def span(self, other: Event, inclusive: bool = False) -> Generator[Event, None, None]:
        assert isinstance(other, Event), f"Can't create span with non-event object {other}"
        assert self.order_id < other.order_id, f"Can't create span from {self} with {other} that does not have a higher order id"
        # If the span is inclusive start with this event, otherwise with the next event
        next_event = self if inclusive else self.next

        while next_event != other:
            current_event = next_event
            next_event = current_event.next
            yield current_event

        # If the span is inclusive, finish with the given target event of the span
        if inclusive:
            yield other

    def compute_event_time(self, encounter_log: EncounterLog):
        """
        Set the epoch time for each event by computing the diff to the begin log event.
        """
        if self.time is None:
            self.time = encounter_log.begin_log.compute_offset_event_time(self.id)
        else:
            self.logger.debug(f"Computing time for event {self} when it is already set")

    def resolve_ability_and_effect_info_references(self, encounter_log: EncounterLog):
        """
        Adds ability info and effect info objects using this events ability id if it has one.
        """
        pass

    def compute_offset_event_time(self, event_id: int) -> datetime:
        """
        Computes the time for the given event id using the millisecond offset encoded in the event ids.
        """
        return self.time + timedelta(milliseconds=(event_id - self.id))

    def _convert_boolean(self, value: str, field_name: str = None) -> bool:
        """
        Convert boolean values encoded as "T" or "F" and log cases where the value is not one of the expected values.
        """
        try:
            bool_value = BooleanType(value)
            return bool_value == BooleanType.TRUE
        except ValueError as e:
            field_name = f"'{field_name}' " if field_name is not None else ""
            self.logger.error(f"Unexpected value when converting field {field_name}to bool! {e}")
