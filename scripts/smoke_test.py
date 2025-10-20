from __future__ import annotations

from datetime import date

from app.db import get_session
from app.models import Aircraft
from app.repository import init_db, list_aircraft, list_flights_in_range, add_aircraft
from app.reporting import generate_flights_summary_pdf


def main() -> None:
    init_db()
    # Ensure there is at least one aircraft for UI usability later
    with get_session() as s:
        aircraft = list_aircraft(s)
        if not aircraft:
            add_aircraft(s, registration="XA-JMA", model="Cessna")

    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year + (1 if today.month == 12 else 0), 1 if today.month == 12 else today.month + 1, 1)
    with get_session() as s:
        flights = list_flights_in_range(s, start, end)
    pdf_path = generate_flights_summary_pdf(flights, start, end)
    print(f"Smoke test OK. PDF: {pdf_path}")


if __name__ == "__main__":
    main()
