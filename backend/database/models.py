from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    components: Mapped[list["Component"]] = relationship(
        back_populates="aircraft",
        cascade="all, delete-orphan"
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="aircraft",
        cascade="all, delete-orphan"
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="aircraft",
        cascade="all, delete-orphan"
    )


class Component(Base):
    __tablename__ = "components"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    aircraft_id: Mapped[str] = mapped_column(
        ForeignKey("aircraft.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    aircraft: Mapped["Aircraft"] = relationship(
        back_populates="components"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    aircraft_id: Mapped[str] = mapped_column(
        ForeignKey("aircraft.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    aircraft: Mapped["Aircraft"] = relationship(
        back_populates="documents"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    aircraft_id: Mapped[str] = mapped_column(
        ForeignKey("aircraft.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    aircraft: Mapped["Aircraft"] = relationship(
        back_populates="conversations"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages"
    )