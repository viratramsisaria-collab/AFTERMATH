
# type: ignore
"""Repository functions for AFTERMATH database operations."""

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.connection import init_db, session_scope
from database.models import (
    CitySave,
    CitySnapshot,
    DecisionRecord,
    EventRecord,
)


def to_jsonable(value):
    """Convert application models into JSON-compatible Python values."""

    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if hasattr(value, "model_dump"):
        return to_jsonable(value.model_dump())

    raise TypeError(f"Cannot serialize {type(value).__name__}.")


def _city_payload(city) -> dict:
    """Serialize a CityState."""

    if hasattr(city, "model_dump"):
        return city.model_dump(mode="json")

    raise TypeError("Expected a Pydantic CityState model.")


def _ensure_save(
    session: Session,
    city,
    save_id: str,
    campaign_id: str | None = None,
) -> CitySave:
    """Create or update a city save inside the current transaction."""

    payload = _city_payload(city)

    record = session.get(CitySave, save_id)

    values = {
        "city_name": city.city_name,
        "campaign_id": campaign_id,
        "day": city.day,
        "population": city.population,
        "budget": city.budget,
        "state": payload,
        "updated_at": datetime.now(timezone.utc),
    }

    if record is None:
        record = CitySave(
            save_id=save_id,
            **values,
        )
        session.add(record)
    else:
        for key, value in values.items():
            if key == "campaign_id" and value is None:
                continue
            setattr(record, key, value)

    session.flush()
    return record


def save_city(
    city,
    save_id: str = "autosave",
    campaign_id: str | None = None,
) -> dict:
    """Save or update a complete city state."""

    init_db()

    with session_scope() as session:
        record = _ensure_save(
            session,
            city,
            save_id,
            campaign_id,
        )

        return {
            "save_id": record.save_id,
            "city_name": record.city_name,
            "day": record.day,
            "population": record.population,
            "budget": record.budget,
        }


def load_city(save_id: str = "autosave"):
    """Restore a saved CityState."""

    from simulation.state import CityState

    init_db()

    with session_scope() as session:
        record = session.get(CitySave, save_id)

        if record is None:
            return None

        return CityState.model_validate(record.state)


def list_city_saves() -> list[dict]:
    """List available city saves."""

    init_db()

    with session_scope() as session:
        records = session.scalars(
            select(CitySave).order_by(CitySave.updated_at.desc())
        ).all()

        return [
            {
                "save_id": record.save_id,
                "city_name": record.city_name,
                "campaign_id": record.campaign_id,
                "day": record.day,
                "population": record.population,
                "budget": record.budget,
                "updated_at": record.updated_at,
            }
            for record in records
        ]


def delete_city_save(save_id: str) -> bool:
    """Delete a city save and its dependent records."""

    init_db()

    with session_scope() as session:
        record = session.get(CitySave, save_id)

        if record is None:
            return False

        session.delete(record)
        return True


def save_snapshot(
    city,
    save_id: str = "autosave",
    campaign_id: str | None = None,
) -> int:
    """Save a historical snapshot of the current city."""

    init_db()

    with session_scope() as session:
        _ensure_save(session, city, save_id, campaign_id)

        metrics = to_jsonable(city.metrics)

        snapshot = CitySnapshot(
            save_id=save_id,
            day=city.day,
            population=city.population,
            budget=city.budget,
            metrics=metrics,
            state=_city_payload(city),
        )

        session.add(snapshot)
        session.flush()

        return snapshot.id


def list_snapshots(save_id: str = "autosave") -> list[dict]:
    """Return snapshots in chronological order."""

    init_db()

    with session_scope() as session:
        records = session.scalars(
            select(CitySnapshot)
            .where(CitySnapshot.save_id == save_id)
            .order_by(CitySnapshot.day.asc(), CitySnapshot.id.asc())
        ).all()

        return [
            {
                "id": item.id,
                "day": item.day,
                "population": item.population,
                "budget": item.budget,
                "metrics": item.metrics,
                "created_at": item.created_at,
            }
            for item in records
        ]


def record_event(
    event,
    save_id: str | None = None,
) -> str:
    """Persist a generated or updated CityEvent."""

    init_db()

    payload = to_jsonable(event)

    event_id = payload["id"]

    with session_scope() as session:
        record = session.get(EventRecord, event_id)

        values = {
            "save_id": save_id,
            "title": payload["title"],
            "category": payload["category"],
            "severity": payload["severity"],
            "district_id": payload.get("district_id"),
            "is_resolved": payload.get("is_resolved", False),
            "payload": payload,
        }

        if record is None:
            record = EventRecord(event_id=event_id, **values)
            session.add(record)
        else:
            for key, value in values.items():
                setattr(record, key, value)

    return event_id


def list_events(
    save_id: str | None = None,
    unresolved_only: bool = False,
) -> list[dict]:
    """Retrieve persisted events."""

    init_db()

    with session_scope() as session:
        statement = select(EventRecord)

        if save_id is not None:
            statement = statement.where(EventRecord.save_id == save_id)

        if unresolved_only:
            statement = statement.where(EventRecord.is_resolved.is_(False))

        statement = statement.order_by(EventRecord.created_at.desc())

        records = session.scalars(statement).all()

        return [
            {
                "event_id": item.event_id,
                "title": item.title,
                "category": item.category,
                "severity": item.severity,
                "district_id": item.district_id,
                "is_resolved": item.is_resolved,
                "payload": item.payload,
            }
            for item in records
        ]


def update_event_status(
    event_id: str,
    is_resolved: bool,
) -> bool:
    """Update the resolution status of an event."""

    init_db()

    with session_scope() as session:
        record = session.get(EventRecord, event_id)

        if record is None:
            return False

        record.is_resolved = is_resolved
        record.payload = {
            **record.payload,
            "is_resolved": is_resolved,
        }

        return True


def record_decision(
    proposal,
    assessment,
    status: str = "pending",
    save_id: str | None = None,
    decision: dict | None = None,
    decision_id: str | None = None,
) -> str:
    """Persist a policy assessment and mayoral decision."""

    allowed_statuses = {
        "pending",
        "approved",
        "rejected",
        "deferred",
    }

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid decision status: {status}"
        )

    init_db()

    proposal_data = to_jsonable(proposal)
    assessment_data = to_jsonable(assessment)
    decision_data = to_jsonable(decision) if decision is not None else None

    identifier = decision_id or f"decision-{uuid4().hex}"

    title = (
        proposal_data.get("title")
        or proposal_data.get("name")
        or "Untitled policy proposal"
    )

    with session_scope() as session:
        record = DecisionRecord(
            decision_id=identifier,
            save_id=save_id,
            proposal_title=title,
            status=status,
            assessment=assessment_data,
            decision=decision_data,
        )

        session.add(record)

    return identifier


def update_decision(
    decision_id: str,
    status: str,
    decision: dict | None = None,
) -> bool:
    """Update the mayor's final decision."""

    allowed_statuses = {
        "pending",
        "approved",
        "rejected",
        "deferred",
    }

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid decision status: {status}"
        )

    init_db()

    with session_scope() as session:
        record = session.get(DecisionRecord, decision_id)

        if record is None:
            return False

        record.status = status

        if decision is not None:
            record.decision = to_jsonable(decision)

        record.updated_at = datetime.now(timezone.utc)

        return True


def list_decisions(
    save_id: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Retrieve persisted policy decisions."""

    init_db()

    with session_scope() as session:
        statement = select(DecisionRecord)

        if save_id is not None:
            statement = statement.where(
                DecisionRecord.save_id == save_id
            )

        if status is not None:
            statement = statement.where(
                DecisionRecord.status == status
            )

        statement = statement.order_by(
            DecisionRecord.created_at.desc()
        )

        records = session.scalars(statement).all()

        return [
            {
                "decision_id": item.decision_id,
                "proposal_title": item.proposal_title,
                "status": item.status,
                "assessment": item.assessment,
                "decision": item.decision,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in records
        ]
