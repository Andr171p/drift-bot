from datetime import datetime

from sqlalchemy import Text, DateTime, BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserOrm(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    role: Mapped[str]

    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'REFEREE', 'PILOT', 'DEVELOPER')",
            "check_role"
        ),
    )


class ReferralOrm(Base):
    __tablename__ = "referrals"

    stage_id: Mapped[int] = mapped_column(
        ForeignKey("stages.id"),
        unique=False,
        nullable=False
    )
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        unique=False,
        nullable=False
    )
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    activated: Mapped[bool]

    stage: Mapped["StageOrm"] = relationship(argument="StageOrm", back_populates="referrals")


class CompetitionOrm(Base):
    __tablename__ = "competitions"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    is_active: Mapped[bool]
    stages_count: Mapped[int]

    stages: Mapped[list["StageOrm"]] = relationship(
        back_populates="competition",
        cascade="all, delete-orphan"
    )


class StageOrm(Base):
    __tablename__ = "stages"

    number: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        unique=False,
        nullable=False
    )
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    location: Mapped[str]
    map_link: Mapped[str | None] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool]

    judges: Mapped[list["JudgesOrm"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )
    pilots: Mapped[list["PilotOrm"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )
    competition: Mapped["CompetitionOrm"] = relationship(
        argument="StageOrm",
        back_populates="stages"
    )


class JudgesOrm(Base):
    __tablename__ = "judges"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), unique=False)
    full_name: Mapped[str]
    criterion: Mapped[str]

    stage: Mapped["StageOrm"] = relationship(argument="StageOrm", back_populates="judges")

    __table_args__ = (
        CheckConstraint("criterion IN ('STYLE', 'ANGLE', 'LINE')", "check_criterion"),
    )


class PilotOrm(Base):
    __tablename__ = "pilots"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), unique=False, nullable=False)
    full_name: Mapped[str]
    age: Mapped[int]
    description: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(unique=True)
    car: Mapped[str]
    number: Mapped[int]

    stage: Mapped["StageOrm"] = relationship(argument="StageOrm", back_populates="pilots")
    qualifications: Mapped[list["QualificationOrm"]] = relationship(back_populates="pilot")


class QualificationOrm(Base):
    __tablename__ = "qualifications"

    pilot_id: Mapped[int] = mapped_column(ForeignKey("pilots.id"), unique=False, nullable=False)
    attempt: Mapped[int]
    angle_points: int
    style_points: int
    line_points: int
    total_points: Mapped[float]

    pilot: Mapped["PilotOrm"] = relationship(argument="PilotOrm", back_populates="qualifications")

    __table_args__ = (
        CheckConstraint("attempt = 1 OR attempt = 2", "check_attempt_count"),
    )
