"""Database layer for telemetry persistence.

Default mode uses local SQLite so the project works out of the box.
Set `DATABASE_URL` to a hosted Postgres URL (Neon/Supabase free tiers) for
cloud persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os
from typing import Iterable

from sqlalchemy import JSON, DateTime, Float, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(120), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    inventory: Mapped[dict] = mapped_column(JSON)
    sales_revenue_usd: Mapped[float] = mapped_column(Float)
    sales_count: Mapped[int] = mapped_column(Integer)
    temperature_c: Mapped[float] = mapped_column(Float)
    payment_status: Mapped[str] = mapped_column(String(20))


def _default_sqlite_url() -> str:
    db_path = Path(__file__).resolve().parent / "vendinsights.db"
    return f"sqlite:///{db_path.as_posix()}"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", _default_sqlite_url())


def _create_engine():
    database_url = get_database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _parse_timestamp(timestamp_value: str) -> datetime:
    normalized = timestamp_value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_timestamp(timestamp_value: datetime) -> str:
    utc_ts = timestamp_value.astimezone(timezone.utc)
    return utc_ts.isoformat().replace("+00:00", "Z")


def count_events() -> int:
    with SessionLocal() as session:
        return session.scalar(select(func.count(TelemetryEvent.id))) or 0


def insert_telemetry_docs(docs: Iterable[dict]) -> int:
    records = []
    for doc in docs:
        records.append(
            TelemetryEvent(
                device_id=doc.get("deviceId", "unknown-device"),
                timestamp=_parse_timestamp(doc["timestamp"]),
                inventory=doc.get("inventory", {}),
                sales_revenue_usd=float(doc.get("sales", {}).get("revenue_usd", 0)),
                sales_count=int(doc.get("sales", {}).get("count", 0)),
                temperature_c=float(doc.get("temperature_c", 0)),
                payment_status=doc.get("payment_status", "ok"),
            )
        )

    if not records:
        return 0

    with SessionLocal() as session:
        session.add_all(records)
        session.commit()
    return len(records)


def replace_telemetry_docs(docs: Iterable[dict]) -> int:
    """Replace all existing telemetry rows with provided docs."""
    with SessionLocal() as session:
        session.query(TelemetryEvent).delete()
        session.commit()

    return insert_telemetry_docs(docs)


def _rows_to_docs(rows: list[TelemetryEvent]) -> list[dict]:
    docs = []
    for row in rows:
        docs.append(
            {
                "timestamp": _format_timestamp(row.timestamp),
                "deviceId": row.device_id,
                "inventory": row.inventory,
                "sales": {
                    "revenue_usd": row.sales_revenue_usd,
                    "count": row.sales_count,
                },
                "temperature_c": row.temperature_c,
                "payment_status": row.payment_status,
            }
        )
    return docs


def fetch_recent_docs(hours: int, machines: int) -> list[dict]:
    """Fetch latest telemetry docs from DB.

    Strategy:
    - select latest active device IDs (up to `machines`)
    - fetch latest `hours` points per selected device
    - return a merged list of documents
    """
    safe_hours = max(1, hours)
    safe_machines = max(1, machines)

    with SessionLocal() as session:
        latest_per_device = session.execute(
            select(
                TelemetryEvent.device_id,
                func.max(TelemetryEvent.timestamp).label("latest_ts"),
            )
            .group_by(TelemetryEvent.device_id)
            .order_by(func.max(TelemetryEvent.timestamp).desc())
        ).all()

        selected_devices = [row[0] for row in latest_per_device[:safe_machines]]
        if not selected_devices:
            return []

        collected_rows: list[TelemetryEvent] = []
        for device_id in selected_devices:
            rows = (
                session.execute(
                    select(TelemetryEvent)
                    .where(TelemetryEvent.device_id == device_id)
                    .order_by(TelemetryEvent.timestamp.desc())
                    .limit(safe_hours)
                )
                .scalars()
                .all()
            )
            rows.reverse()
            collected_rows.extend(rows)

    return _rows_to_docs(collected_rows)
