from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def create_alloydb_engine(
    instance_connection_name: str,
    user: str,
    password: str,
    database: str,
    ip_type: str = "PRIVATE",
):
    try:
        from google.cloud import alloydb_connector
    except ImportError as exc:
        raise RuntimeError(
            "Install google-cloud-alloydb-connector to use AlloyDB connector support"
        ) from exc

    connector_obj = alloydb_connector.AlloyDBConnector()

    def getconn():
        return connector_obj.connect(
            instance_connection_name,
            "pg8000",
            user=user,
            password=password,
            db=database,
            ip_type=ip_type,
        )

    return create_engine("postgresql+pg8000://", creator=getconn, future=True)


class WellnessEntryORM(Base):
    __tablename__ = "wellness_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False, index=True)
    mood = Column(Integer, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    exercise_minutes = Column(Integer, nullable=False)
    water_glasses = Column(Integer, nullable=False)
    meditation_minutes = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    notes = Column(Text, nullable=False, default="")


@dataclass
class WellnessEntry:
    date: str
    mood: int
    sleep_hours: float
    exercise_minutes: int
    water_glasses: int
    meditation_minutes: int
    stress_level: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_orm(cls, orm: WellnessEntryORM) -> "WellnessEntry":
        return cls(
            date=orm.date,
            mood=orm.mood,
            sleep_hours=orm.sleep_hours,
            exercise_minutes=orm.exercise_minutes,
            water_glasses=orm.water_glasses,
            meditation_minutes=orm.meditation_minutes,
            stress_level=orm.stress_level,
            notes=orm.notes,
        )


class WellnessManager:
    def __init__(
        self,
        storage_path: Path | str = "wellness_data.json",
        db_url: str | None = None,
    ):
        self.storage_path = Path(storage_path)
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.alloydb_instance_connection_name = os.environ.get("ALLOYDB_INSTANCE_CONNECTION_NAME")
        self.alloydb_user = os.environ.get("ALLOYDB_USER")
        self.alloydb_password = os.environ.get("ALLOYDB_PASSWORD")
        self.alloydb_database = os.environ.get("ALLOYDB_DATABASE")
        self.alloydb_ip_type = os.environ.get("ALLOYDB_IP_TYPE", "PRIVATE")
        self.db_enabled = False
        self.entries: list[WellnessEntry] = []

        if (
            self.alloydb_instance_connection_name
            and self.alloydb_user
            and self.alloydb_password
            and self.alloydb_database
        ):
            try:
                self.engine = create_alloydb_engine(
                    self.alloydb_instance_connection_name,
                    self.alloydb_user,
                    self.alloydb_password,
                    self.alloydb_database,
                    ip_type=self.alloydb_ip_type,
                )
                self.Session = sessionmaker(self.engine, future=True)
                Base.metadata.create_all(self.engine)
                self.db_enabled = True
            except Exception:
                self.db_enabled = False
                self.load()
        elif self.db_url:
            try:
                self.engine = create_engine(self.db_url, future=True)
                self.Session = sessionmaker(self.engine, future=True)
                Base.metadata.create_all(self.engine)
                self.db_enabled = True
            except SQLAlchemyError:
                self.db_enabled = False
                self.load()
        else:
            self.load()

    def load(self) -> None:
        if not self.storage_path.exists():
            self.entries = []
            return
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.entries = [WellnessEntry(**item) for item in raw]
        except (json.JSONDecodeError, TypeError, ValueError):
            self.entries = []

    def save(self) -> None:
        self.storage_path.write_text(
            json.dumps([entry.to_dict() for entry in self.entries], indent=2),
            encoding="utf-8",
        )

    def add_entry(
        self,
        mood: int,
        sleep_hours: float,
        exercise_minutes: int,
        water_glasses: int,
        meditation_minutes: int,
        stress_level: int,
        notes: str = "",
        date: str | None = None,
    ) -> WellnessEntry:
        entry_date = date or datetime.now().strftime("%Y-%m-%d")
        if self.db_enabled:
            with self.Session() as session:
                entity = WellnessEntryORM(
                    date=entry_date,
                    mood=mood,
                    sleep_hours=sleep_hours,
                    exercise_minutes=exercise_minutes,
                    water_glasses=water_glasses,
                    meditation_minutes=meditation_minutes,
                    stress_level=stress_level,
                    notes=notes,
                )
                session.add(entity)
                session.commit()
                session.refresh(entity)
                return WellnessEntry.from_orm(entity)

        entry = WellnessEntry(
            date=entry_date,
            mood=mood,
            sleep_hours=sleep_hours,
            exercise_minutes=exercise_minutes,
            water_glasses=water_glasses,
            meditation_minutes=meditation_minutes,
            stress_level=stress_level,
            notes=notes,
        )
        self.entries.append(entry)
        self.save()
        return entry

    def list_entries(self) -> list[WellnessEntry]:
        if self.db_enabled:
            try:
                with self.Session() as session:
                    rows = session.query(WellnessEntryORM).order_by(WellnessEntryORM.date.desc()).all()
                    return [WellnessEntry.from_orm(row) for row in rows]
            except SQLAlchemyError:
                return []

        return sorted(self.entries, key=lambda entry: entry.date, reverse=True)

    def get_summary(self) -> dict[str, Any]:
        entries = self.list_entries()
        if not entries:
            return {
                "count": 0,
                "average_mood": None,
                "average_sleep_hours": None,
                "average_exercise_minutes": None,
                "average_water_glasses": None,
                "average_meditation_minutes": None,
                "average_stress_level": None,
            }

        sorted_entries = sorted(entries, key=lambda entry: entry.date)
        return {
            "count": len(sorted_entries),
            "average_mood": mean(entry.mood for entry in sorted_entries),
            "average_sleep_hours": mean(entry.sleep_hours for entry in sorted_entries),
            "average_exercise_minutes": mean(entry.exercise_minutes for entry in sorted_entries),
            "average_water_glasses": mean(entry.water_glasses for entry in sorted_entries),
            "average_meditation_minutes": mean(entry.meditation_minutes for entry in sorted_entries),
            "average_stress_level": mean(entry.stress_level for entry in sorted_entries),
        }

    def get_trends(self) -> dict[str, list[tuple[str, float]]]:
        sorted_entries = sorted(self.list_entries(), key=lambda entry: entry.date)
        return {
            "mood": [(entry.date, float(entry.mood)) for entry in sorted_entries],
            "sleep": [(entry.date, entry.sleep_hours) for entry in sorted_entries],
            "stress": [(entry.date, float(entry.stress_level)) for entry in sorted_entries],
            "exercise": [(entry.date, float(entry.exercise_minutes)) for entry in sorted_entries],
            "water": [(entry.date, float(entry.water_glasses)) for entry in sorted_entries],
            "meditation": [(entry.date, float(entry.meditation_minutes)) for entry in sorted_entries],
        }
