from datetime import datetime

from sqlalchemy import Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RaceOrm(Base):
    __tablename__ = "races"

    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    place: Mapped[str]
    map_link: Mapped[str | None] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    check_in: bool
    active: bool

    referees: Mapped[list["RefereeOrm"]] = relationship(back_populates="race")
    pilots: Mapped[list["PilotOrm"]] = relationship(back_populates="race")


class RefereeOrm(Base):
    __tablename__ = "referees"

    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), unique=False)
    full_name: Mapped[str]
    criterion: Mapped[str]

    race: Mapped["RaceOrm"] = relationship(argument="RaceOrm", back_populates="referees")

    __table_args__ = (
        CheckConstraint("criterion IN ('STYLE', 'ANGLE', 'LINE')", "check_criterion"),
    )


class PilotOrm(Base):
    __tablename__ = "pilots"

    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), unique=False, nullable=False)
    full_name: Mapped[str]
    age: Mapped[int]
    description: Mapped[str] = mapped_column(Text)
    car: Mapped[str]
    number: Mapped[int]

    race: Mapped["RaceOrm"] = relationship(argument="RaceOrm", back_populates="pilots")
    qualifications: Mapped[list["QualificationOrm"]] = relationship(back_populates="pilot")


class QualificationOrm(Base):
    __tablename__ = "qualifications"

    pilot_id: Mapped[int] = mapped_column(ForeignKey("pilots.id"), unique=False, nullable=False)
    attempt: Mapped[int]
    points: Mapped[float]

    pilot: Mapped["PilotOrm"] = relationship(argument="PilotOrm", back_populates="qualifications")

    __table_args__ = (
        CheckConstraint("attempt = 1 OR attempt = 2", "check_attempt_count"),
    )
