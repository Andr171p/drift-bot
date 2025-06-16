from datetime import datetime

from sqlalchemy import Text, DateTime, BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserOrm(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    role: Mapped[str]

    referrals: Mapped[list["ReferralOrm"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint("role IN ('ADMIN', 'REFEREE', 'PILOT')", "check_role"),
    )


class ReferralOrm(Base):
    __tablename__ = "referrals"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        unique=False,
        nullable=False
    )
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id"),
        unique=False,
        nullable=False
    )
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped["UserOrm"] = relationship(argument="UserOrm", back_populates="referrals")
    event: Mapped["EventOrm"] = relationship(argument="EventOrm", back_populates="referrals")


class EventOrm(Base):
    __tablename__ = "events"

    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    place: Mapped[str]
    map_link: Mapped[str | None] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    active: bool

    referees: Mapped[list["RefereeOrm"]] = relationship(back_populates="event")
    pilots: Mapped[list["PilotOrm"]] = relationship(back_populates="event")
    referrals: Mapped[list["ReferralOrm"]] = relationship(back_populates="event")


class RefereeOrm(Base):
    __tablename__ = "referees"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), unique=False)
    full_name: Mapped[str]
    criterion: Mapped[str]

    event: Mapped["EventOrm"] = relationship(argument="EventOrm", back_populates="referees")

    __table_args__ = (
        CheckConstraint("criterion IN ('STYLE', 'ANGLE', 'LINE')", "check_criterion"),
    )


class PilotOrm(Base):
    __tablename__ = "pilots"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), unique=False, nullable=False)
    full_name: Mapped[str]
    age: Mapped[int]
    description: Mapped[str] = mapped_column(Text)
    car: Mapped[str]
    number: Mapped[int]

    event: Mapped["EventOrm"] = relationship(argument="EventOrm", back_populates="pilots")
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
