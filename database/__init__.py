
"""AFTERMATH database package."""

from database.connection import (
    Base,
    close_database,
    get_engine,
    init_db,
    session_scope,
)
from database.repository import (
    delete_city_save,
    list_city_saves,
    list_decisions,
    list_events,
    list_snapshots,
    load_city,
    record_decision,
    record_event,
    save_city,
    save_snapshot,
    update_decision,
    update_event_status,
)

__all__ = [
    "Base",
    "close_database",
    "get_engine",
    "init_db",
    "session_scope",
    "save_city",
    "load_city",
    "list_city_saves",
    "delete_city_save",
    "save_snapshot",
    "list_snapshots",
    "record_event",
    "list_events",
    "update_event_status",
    "record_decision",
    "update_decision",
    "list_decisions",
]
