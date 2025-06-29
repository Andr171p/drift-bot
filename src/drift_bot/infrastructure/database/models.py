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
            "role IN ('ADMIN', 'JUDGE', 'PILOT', 'DEVELOPER')",
            "check_user_role"
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

    judges: Mapped[list["JudgeOrm"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )
    pilots: Mapped[list["PilotOrm"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )
    championship: Mapped["ChampionshipOrm"] = relationship(back_populates="stages")


class JudgeOrm(Base):
    __tablename__ = "judges"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), unique=False)
    full_name: Mapped[str]
    criterion: Mapped[str]

    files: Mapped[list["FileMetadataOrm"]] = relationship(
        primaryjoin="""and_(JudgeOrm.id == foreign(FileMetadataOrm.parent_id), 
        FileMetadataOrm.parent_type == 'judge')""",
        cascade="all, delete-orphan"
    )

    stage: Mapped["StageOrm"] = relationship(back_populates="judges")

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


class PilotOrm(Base):
    __tablename__ = "pilots"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), unique=False, nullable=False)
    full_name: Mapped[str]
    age: Mapped[int]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cars: Mapped[list["CarOrm"]] = relationship(back_populates="pilot")
    number: Mapped[int]

    files: Mapped[list["FileMetadataOrm"]] = relationship(
        primaryjoin="""and_(PilotOrm.id == foreign(FileMetadataOrm.parent_id), 
        FileMetadataOrm.parent_type == 'pilot')""",
        cascade="all, delete-orphan"
    )

    stage: Mapped["StageOrm"] = relationship(back_populates="pilots")
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
