from __future__ import annotations

from datetime import date, time
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from .db import Base, engine
from .models import Aircraft, Client, FlightLog, FlightSupply, Supply, Mechanic, ServiceType, Concept


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Lightweight migrations for existing SQLite DBs
    with engine.begin() as conn:
        # FlightLog: service_type (VARCHAR), service_time (TIME)
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info('flight_logs')").fetchall()}
        if 'service_type' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_logs ADD COLUMN service_type VARCHAR(60)")
        if 'service_time' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_logs ADD COLUMN service_time TIME")
        # FlightSupply: viaticos (NUMERIC)
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info('flight_supplies')").fetchall()}
        if 'viaticos' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_supplies ADD COLUMN viaticos NUMERIC(12,2) DEFAULT 0")
        # New catalogs tables may not exist if metadata.create_all didn't create them (older DB)
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS mechanics (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(120) NOT NULL, UNIQUE(name))")
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS service_types (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(120) NOT NULL, UNIQUE(name))")
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS concepts (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(150) NOT NULL, UNIQUE(name))")
        # Add nullable FKs in flight_logs
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info('flight_logs')").fetchall()}
        if 'mechanic_id' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_logs ADD COLUMN mechanic_id INTEGER REFERENCES mechanics(id)")
        if 'service_type_id' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_logs ADD COLUMN service_type_id INTEGER REFERENCES service_types(id)")
        if 'concept_id' not in cols:
            conn.exec_driver_sql("ALTER TABLE flight_logs ADD COLUMN concept_id INTEGER REFERENCES concepts(id)")


# Generic helpers
def list_clients(session: Session) -> List[Client]:
    return list(session.scalars(select(Client).order_by(Client.name)))


def add_client(session: Session, name: str, rfc: str | None = None, phone: str | None = None, email: str | None = None, notes: str | None = None) -> Client:
    c = Client(name=name, rfc=rfc, phone=phone, email=email, notes=notes)
    session.add(c)
    session.flush()
    return c


def delete_client(session: Session, client_id: int) -> None:
    obj = session.get(Client, client_id)
    if obj:
        session.delete(obj)


def list_supplies(session: Session) -> List[Supply]:
    return list(session.scalars(select(Supply).order_by(Supply.name)))


def add_supply(session: Session, name: str, unit: str, cost_per_unit: float, notes: str | None = None) -> Supply:
    s = Supply(name=name, unit=unit, cost_per_unit=cost_per_unit, notes=notes)
    session.add(s)
    session.flush()
    return s


def delete_supply(session: Session, supply_id: int) -> None:
    obj = session.get(Supply, supply_id)
    if obj:
        session.delete(obj)


def list_aircraft(session: Session) -> List[Aircraft]:
    return list(session.scalars(select(Aircraft).order_by(Aircraft.registration)))


# New catalogs CRUD
def list_mechanics(session: Session) -> List[Mechanic]:
    return list(session.scalars(select(Mechanic).order_by(Mechanic.name)))


def add_mechanic(session: Session, name: str) -> Mechanic:
    m = Mechanic(name=name)
    session.add(m)
    session.flush()
    return m


def list_service_types(session: Session) -> List[ServiceType]:
    return list(session.scalars(select(ServiceType).order_by(ServiceType.name)))


def add_service_type(session: Session, name: str) -> ServiceType:
    st = ServiceType(name=name)
    session.add(st)
    session.flush()
    return st


def list_concepts(session: Session) -> List[Concept]:
    return list(session.scalars(select(Concept).order_by(Concept.name)))


def add_concept(session: Session, name: str) -> Concept:
    c = Concept(name=name)
    session.add(c)
    session.flush()
    return c


def add_aircraft(session: Session, registration: str, model: str | None = None) -> Aircraft:
    a = Aircraft(registration=registration, model=model)
    session.add(a)
    session.flush()
    return a


def list_flights_in_range(session: Session, start: date, end: date) -> List[FlightLog]:
    stmt = (
        select(FlightLog)
        .options(
            selectinload(FlightLog.aircraft),
            selectinload(FlightLog.client),
            selectinload(FlightLog.mechanic),
            selectinload(FlightLog.service_type_ref),
            selectinload(FlightLog.concept),
            selectinload(FlightLog.supplies).selectinload(FlightSupply.supply),
        )
        .where(FlightLog.flight_date.between(start, end))
        .order_by(FlightLog.flight_date)
    )
    return list(session.scalars(stmt))


def add_flight(
    session: Session,
    flight_date: date,
    aircraft_id: int,
    client_id: int | None,
    pilot: str,
    copilot: str | None,
    origin: str,
    destination: str,
    flight_minutes: int,
    landings: int,
    notes: str | None = None,
    service_type: str | None = None,
    service_time: time | None = None,
    mechanic_id: int | None = None,
    service_type_id: int | None = None,
    concept_id: int | None = None,
) -> FlightLog:
    f = FlightLog(
        flight_date=flight_date,
        aircraft_id=aircraft_id,
        client_id=client_id,
        pilot=pilot,
        copilot=copilot,
        origin=origin,
        destination=destination,
        service_type=service_type,
        service_time=service_time,
        mechanic_id=mechanic_id,
        service_type_id=service_type_id,
        concept_id=concept_id,
        flight_minutes=flight_minutes,
        landings=landings,
        notes=notes,
    )
    session.add(f)
    session.flush()
    return f


def add_flight_supply(session: Session, flight_id: int, supply_id: int, quantity: float, unit_cost: float, viaticos: float = 0.0) -> FlightSupply:
    item = FlightSupply(
        flight_id=flight_id,
        supply_id=supply_id,
        quantity=quantity,
        unit_cost=unit_cost,
        viaticos=viaticos,
    )
    session.add(item)
    session.flush()
    return item

