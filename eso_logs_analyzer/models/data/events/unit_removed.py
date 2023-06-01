from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded


class UnitRemoved(Event):
    event_type: str = "UNIT_REMOVED"

    def __init__(self, event_id: int, unit_id: str):
        super(UnitRemoved, self).__init__(event_id)
        # Id of the unit that was removed
        self.unit_id = int(unit_id)

        # Corresponding unit added event
        self.unit_added: UnitAdded = None

    # def __str__(self):
    #     return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, " \
    #            f"unit_added={self.unit_added is not None})"
    #
    # __repr__ = __str__
