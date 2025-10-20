from __future__ import annotations

from datetime import date, time
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    rfc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    flights: Mapped[List["FlightLog"]] = relationship(back_populates="client")

    __table_args__ = (UniqueConstraint("name", name="uq_clients_name"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Client(id={self.id}, name={self.name!r})"


class Supply(Base):
    __tablename__ = "supplies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default="unidad")
    cost_per_unit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    notes: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    items: Mapped[List["FlightSupply"]] = relationship(back_populates="supply")

    __table_args__ = (UniqueConstraint("name", name="uq_supplies_name"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Supply(id={self.id}, name={self.name!r})"


class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    registration: Mapped[str] = mapped_column(String(20), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    owner: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    flights: Mapped[List["FlightLog"]] = relationship(back_populates="aircraft")

    __table_args__ = (UniqueConstraint("registration", name="uq_aircraft_registration"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Aircraft(id={self.id}, reg={self.registration!r})"


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    __table_args__ = (UniqueConstraint("name", name="uq_mechanics_name"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Mechanic(id={self.id}, name={self.name!r})"


class ServiceType(Base):
    __tablename__ = "service_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    __table_args__ = (UniqueConstraint("name", name="uq_service_types_name"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ServiceType(id={self.id}, name={self.name!r})"


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    __table_args__ = (UniqueConstraint("name", name="uq_concepts_name"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Concept(id={self.id}, name={self.name!r})"


class FlightLog(Base):
    __tablename__ = "flight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_date: Mapped[date] = mapped_column(Date, nullable=False)

    aircraft_id: Mapped[int] = mapped_column(ForeignKey("aircraft.id"), nullable=False)
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True)

    pilot: Mapped[str] = mapped_column(String(120), nullable=False)
    copilot: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    origin: Mapped[str] = mapped_column(String(10), nullable=False)
    destination: Mapped[str] = mapped_column(String(10), nullable=False)
    departure_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    arrival_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    # Campos para reportes de PRE/POST y servicios
    service_type: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)  # legacy string, mirror of ServiceType
    service_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    # Catalog references
    mechanic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mechanics.id"), nullable=True)
    service_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("service_types.id"), nullable=True)
    concept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("concepts.id"), nullable=True)
    flight_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    landings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    aircraft: Mapped[Aircraft] = relationship(back_populates="flights")
    client: Mapped[Optional[Client]] = relationship(back_populates="flights")
    supplies: Mapped[List["FlightSupply"]] = relationship(back_populates="flight", cascade="all, delete-orphan")
    mechanic: Mapped[Optional[Mechanic]] = relationship()
    service_type_ref: Mapped[Optional[ServiceType]] = relationship()
    concept: Mapped[Optional[Concept]] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"FlightLog(id={self.id}, date={self.flight_date})"


class FlightSupply(Base):
    __tablename__ = "flight_supplies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flight_logs.id"), nullable=False)
    supply_id: Mapped[int] = mapped_column(ForeignKey("supplies.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    viaticos: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    flight: Mapped[FlightLog] = relationship(back_populates="supplies")
    supply: Mapped[Supply] = relationship(back_populates="items")

    @property
    def total_cost(self) -> float:
        try:
            return float(self.quantity) * float(self.unit_cost)
        except Exception:
            return 0.0
