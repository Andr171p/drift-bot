from datetime import datetime

from sqlalchemy import Text, DateTime, BigInteger, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserOrm(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    role: Mapped[str]

    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'JUDGE', 'PILOT', 'DEVELOPER')",
            "check_user_role"
        ),
        Index("user_id_index", "user_id"),
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


class FileMetadataOrm(Base):
    __tablename__ = "file_metadata"

    key: Mapped[str]
    bucket: Mapped[str]
    size: Mapped[float]
    format: Mapped[str]
    type: Mapped[str]
    uploaded_date: Mapped[datetime] = mapped_column(DateTime)

    parent_type: Mapped[str]
    parent_id: Mapped[int]


class ChampionshipOrm(Base):
    __tablename__ = "championships"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]
    stages_count: Mapped[int]

    files: Mapped[list["FileMetadataOrm"]] = relationship(
        primaryjoin="""and_(ChampionshipOrm.id == foreign(FileMetadataOrm.parent_id), 
        FileMetadataOrm.parent_type == 'championship')""",
        cascade="all, delete-orphan",
        lazy="select"
    )

    stages: Mapped[list["StageOrm"]] = relationship(
        back_populates="championship",
        cascade="all, delete-orphan"
    )


class StageOrm(Base):
    __tablename__ = "stages"

    championship_id: Mapped[int] = mapped_column(
        ForeignKey("championships.id"),
        unique=False,
        nullable=False
    )
    number: Mapped[int]
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str]
    map_link: Mapped[str | None] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool]

    files: Mapped[list["FileMetadataOrm"]] = relationship(
        primaryjoin="""and_(StageOrm.id == foreign(FileMetadataOrm.parent_id),  
        FileMetadataOrm.parent_type == 'stage')""",
        cascade="all, delete-orphan",
        lazy="select"
    )

    participants: Mapped[list["ParticipantOrm"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )
    championship: Mapped["ChampionshipOrm"] = relationship(back_populates="stages")


class ParticipantOrm(Base):
    __tablename__ = "participants"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), unique=False)
    full_name: Mapped[str]

    type: Mapped[str] = mapped_column(nullable=False)

    files: Mapped[list["FileMetadataOrm"]] = relationship(
        primaryjoin="""and_(
            ParticipantOrm.id == foreign(FileMetadataOrm.parent_id),
            FileMetadataOrm.parent_type == 'participant'
        )""",
        cascade="all, delete-orphan"
    )
    stage: Mapped["StageOrm"] = relationship(back_populates="participants")

    __mapper_args__ = {
        "polymorphic_identity": "participant",
        "polymorphic_on": type
    }

    __table_args__ = (
        Index("user_stage_index", "user_id", "stage_id", unique=True),
    )


class JudgeOrm(ParticipantOrm):
    __tablename__ = "judges"

    criterion: Mapped[str]

    __table_args__ = (
        CheckConstraint("criterion IN ('STYLE', 'ANGLE', 'LINE')", "check_criterion"),
    )


class CarOrm(Base):
    __tablename__ = "cars"

    pilot_id: Mapped[int] = mapped_column(ForeignKey("pilots.id"), unique=False)
    type: Mapped[str]
    plate: Mapped[str | None] = mapped_column(nullable=True)
    hp: Mapped[int]

    pilot: Mapped["PilotOrm"] = relationship(back_populates="cars")


class PilotOrm(ParticipantOrm):
    __tablename__ = "pilots"

    age: Mapped[int]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cars: Mapped[list["CarOrm"]] = relationship(back_populates="pilot")
    number: Mapped[int]

    qualifications: Mapped[list["QualificationOrm"]] = relationship(back_populates="pilot")


class QualificationOrm(Base):
    __tablename__ = "qualifications"

    pilot_id: Mapped[int] = mapped_column(ForeignKey("pilots.id"), unique=False, nullable=False)
    attempt: Mapped[int]
    angle_points: Mapped[float]
    style_points: Mapped[float]
    line_points: Mapped[float]
    total_points: Mapped[float]

    pilot: Mapped["PilotOrm"] = relationship(back_populates="qualifications")

    __table_args__ = (
        CheckConstraint("attempt = 1 OR attempt = 2", "check_attempt_count"),
    )
