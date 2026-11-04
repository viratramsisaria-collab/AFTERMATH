
"""SQLAlchemy models for AFTERMATH persistence."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from database.connection import Base


def utc_now():
    return datetime.now(timezone.utc)


class CitySave(Base):
    """Complete saved state of a city."""

    __tablename__ = "city_saves"

    save_id = Column(String(100), primary_key=True)
    city_name = Column(String(120), nullable=False)
    campaign_id = Column(String(100), nullable=True)
    day = Column(Integer, nullable=False, default=1)
    population = Column(Integer, nullable=False, default=0)
    budget = Column(Float, nullable=False, default=0.0)
    state = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class CitySnapshot(Base):
    """Historical snapshot of a city's simulation state."""

    __tablename__ = "city_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    save_id = Column(
        String(100),
        ForeignKey("city_saves.save_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day = Column(Integer, nullable=False, index=True)
    population = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)
    state = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class EventRecord(Base):
    """Persisted simulation event."""

    __tablename__ = "event_records"

    event_id = Column(String(120), primary_key=True)
    save_id = Column(
        String(100),
        ForeignKey("city_saves.save_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title = Column(String(200), nullable=False)
    category = Column(String(60), nullable=False)
    severity = Column(String(60), nullable=False)
    district_id = Column(String(100), nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class DecisionRecord(Base):
    """Persisted mayoral policy decision."""

    __tablename__ = "decision_records"

    decision_id = Column(String(120), primary_key=True)
    save_id = Column(
        String(100),
        ForeignKey("city_saves.save_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    proposal_title = Column(String(200), nullable=False)
    status = Column(String(40), nullable=False, default="pending")
    assessment = Column(JSON, nullable=False)
    decision = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
