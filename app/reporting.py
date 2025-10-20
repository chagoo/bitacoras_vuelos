from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .config import REPORTS_DIR
from .models import FlightLog
from .company_config import load_company_config


def generate_flights_summary_pdf(flights: List[FlightLog], start: date, end: date) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = REPORTS_DIR / f"reporte_vuelos_{start.isoformat()}_a_{end.isoformat()}.pdf"

    c = canvas.Canvas(str(filename), pagesize=LETTER)
    width, height = LETTER

    # Header with company
    cfg = load_company_config()
    if cfg.logo_path:
        try:
            c.drawImage(cfg.logo_path, 0.8 * inch, height - 1.2 * inch, width=1.2 * inch, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2.2 * inch, height - 1.0 * inch, cfg.name or "Reporte de Vuelos")
    c.setFont("Helvetica", 10)
    c.drawString(2.2 * inch, height - 1.2 * inch, f"Periodo: {start.isoformat()} a {end.isoformat()}")

    # Table header
    y = height - 1.6 * inch
    c.setFont("Helvetica-Bold", 9)
    headers = ["Fecha", "Matrícula", "Cliente", "Piloto", "Origen", "Destino", "Minutos", "Aterrizajes"]
    x_positions = [1, 1.9, 2.8, 4.1, 5.1, 5.8, 6.5, 7.2]
    for h, x in zip(headers, x_positions):
        c.drawString(x * inch, y, h)
    y -= 0.2 * inch
    c.setFont("Helvetica", 9)

    total_minutes = 0
    total_landings = 0

    for f in flights:
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch
            c.setFont("Helvetica-Bold", 9)
            for h, x in zip(headers, x_positions):
                c.drawString(x * inch, y, h)
            y -= 0.2 * inch
            c.setFont("Helvetica", 9)

        c.drawString(1 * inch, y, f.flight_date.isoformat())
        c.drawString(1.9 * inch, y, f.aircraft.registration if f.aircraft else "-")
        c.drawString(2.8 * inch, y, (f.client.name if f.client else "-")[:20])
        c.drawString(4.1 * inch, y, (f.pilot or "-")[:15])
        c.drawString(5.1 * inch, y, (f.origin or "-")[:5])
        c.drawString(5.8 * inch, y, (f.destination or "-")[:5])
        c.drawRightString(7.0 * inch, y, str(f.flight_minutes))
        c.drawRightString(7.7 * inch, y, str(f.landings))
        y -= 0.18 * inch
        total_minutes += int(f.flight_minutes or 0)
        total_landings += int(f.landings or 0)

    # Totals
    y -= 0.2 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5.1 * inch, y, "Totales:")
    c.drawRightString(7.0 * inch, y, str(total_minutes))
    c.drawRightString(7.7 * inch, y, str(total_landings))

    c.showPage()
    c.save()
    return filename


def generate_bitacora_pre_post_pdf(
    flights: List[FlightLog], month: int, year: int, client_name: str, matricula: str
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = REPORTS_DIR / f"bitacora_pre_post_{matricula}_{year}_{month:02d}.pdf"
    c = canvas.Canvas(str(filename), pagesize=LETTER)
    width, height = LETTER

    # Encabezado
    cfg = load_company_config()
    if cfg.logo_path:
        try:
            c.drawImage(cfg.logo_path, 0.8 * inch, height - 1.3 * inch, width=1.2 * inch, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.2 * inch, height - 0.8 * inch, (cfg.name or "").upper())
    c.setFont("Helvetica", 9)
    if cfg.afac_no:
        c.drawString(2.2 * inch, height - 1.0 * inch, f"TALLER AERONAUTICO AUTORIZADO AFAC No. {cfg.afac_no}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 1.3 * inch, "BITACORA DE PRE Y POST VUELOS")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.55 * inch, f"MES {month:02d}    AÑO {year}")
    c.drawString(4.5 * inch, height - 1.55 * inch, f"CLIENTE  {client_name}")
    c.drawString(4.5 * inch, height - 1.75 * inch, f"MATRICULA  {matricula}")

    # Encabezados de tabla
    y = height - 2.1 * inch
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(1 * inch, y - 0.18 * inch, 6.6 * inch, 0.25 * inch, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    headers = ["FECHA VUELO", "HORA", "TIPO DE SERVICIO", "OBSERVACIONES"]
    x_positions = [1, 2.3, 3.2, 4.4]
    for h, x in zip(headers, x_positions):
        c.drawString(x * inch, y, h)
    y -= 0.35 * inch

    c.setFont("Helvetica", 10)
    for f in flights:
        if f.flight_date.month != month or f.flight_date.year != year:
            continue
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch
        c.drawString(1 * inch, y, f.flight_date.strftime("%d/%m/%Y"))
        if f.service_time:
            c.drawString(2.3 * inch, y, f.service_time.strftime("%I:%M %p").lower())
        st = f.service_type or (getattr(f, 'service_type_ref', None).name if getattr(f, 'service_type_ref', None) else "")
        c.drawString(3.2 * inch, y, (st or "").upper())
        c.drawString(4.4 * inch, y, (f.notes or "")[:60])
        y -= 0.35 * inch

    c.showPage()
    c.save()
    return filename


def generate_consumibles_servicios_pdf(
    flights: List[FlightLog],
    month: int,
    year: int,
    client_name: str,
    matricula: str,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = REPORTS_DIR / f"consumibles_servicios_{matricula}_{year}_{month:02d}.pdf"
    c = canvas.Canvas(str(filename), pagesize=LETTER)
    width, height = LETTER

    # Header
    cfg = load_company_config()
    if cfg.logo_path:
        try:
            c.drawImage(cfg.logo_path, 0.8 * inch, height - 1.3 * inch, width=1.2 * inch, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.2 * inch, height - 0.8 * inch, (cfg.name or "").upper())
    c.setFont("Helvetica", 9)
    if cfg.afac_no:
        c.drawString(2.2 * inch, height - 1.0 * inch, f"TALLER AERONAUTICO AUTORIZADO AFAC No. {cfg.afac_no}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 1.3 * inch, "SUMINISTRO DE CONSUMIBLES Y SERVICIOS EN PRE Y POST VUELOS")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.55 * inch, f"MES {month:02d}    AÑO {year}")
    c.drawString(4.5 * inch, height - 1.55 * inch, f"CLIENTE  {client_name}")
    c.drawString(4.5 * inch, height - 1.75 * inch, f"MATRICULA  {matricula}")

    # Table header
    y = height - 2.1 * inch
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(1 * inch, y - 0.18 * inch, 6.6 * inch, 0.25 * inch, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    headers = ["FECHA VUELO", "HORA", "TIPO DE SERVICIO", "CONCEPTO", "CANT.", "PRECIO", "SUBTOTAL", "VIATICOS", "IMPORTE"]
    x = [1, 2.1, 2.9, 4.0, 5.3, 5.7, 6.2, 6.7, 7.2]
    for h, xp in zip(headers, x):
        c.drawString(xp * inch, y, h)
    y -= 0.3 * inch

    c.setFont("Helvetica", 9)
    subtotal = 0.0
    total_viaticos = 0.0

    for f in flights:
        if f.flight_date.month != month or f.flight_date.year != year:
            continue
        # If no supplies, print service row only with zeros
        items = f.supplies or []
        if not items:
            if y < 1 * inch:
                c.showPage(); y = height - 1 * inch
            c.drawString(1 * inch, y, f.flight_date.strftime("%d/%m/%Y"))
            if f.service_time:
                c.drawString(2.1 * inch, y, f.service_time.strftime("%I:%M %p").lower())
            st = f.service_type or (getattr(f, 'service_type_ref', None).name if getattr(f, 'service_type_ref', None) else "")
            c.drawString(2.9 * inch, y, (st or "").upper()[:18])
            c.drawString(4.0 * inch, y, "HORAS EXTRAS")
            c.drawRightString(5.6 * inch, y, "0")
            c.drawRightString(6.1 * inch, y, "$0.00")
            c.drawRightString(6.6 * inch, y, "$0.00")
            c.drawRightString(7.1 * inch, y, "$0.00")
            c.drawRightString(7.6 * inch, y, "$0.00")
            y -= 0.25 * inch
            continue

        for it in items:
            if y < 1 * inch:
                c.showPage(); y = height - 1 * inch
            c.drawString(1 * inch, y, f.flight_date.strftime("%d/%m/%Y"))
            if f.service_time:
                c.drawString(2.1 * inch, y, f.service_time.strftime("%I:%M %p").lower())
            st = f.service_type or (getattr(f, 'service_type_ref', None).name if getattr(f, 'service_type_ref', None) else "")
            c.drawString(2.9 * inch, y, (st or "").upper()[:18])
            c.drawString(4.0 * inch, y, it.supply.name[:22])
            c.drawRightString(5.6 * inch, y, f"{float(it.quantity):.0f}")
            c.drawRightString(6.1 * inch, y, f"${float(it.unit_cost):,.2f}")
            sub = float(it.quantity) * float(it.unit_cost)
            c.drawRightString(6.6 * inch, y, f"${sub:,.2f}")
            c.drawRightString(7.1 * inch, y, f"${float(it.viaticos):,.2f}")
            total = sub + float(it.viaticos)
            c.drawRightString(7.6 * inch, y, f"${total:,.2f}")
            subtotal += sub
            total_viaticos += float(it.viaticos)
            y -= 0.25 * inch

    # Totales al pie
    y -= 0.2 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(6.6 * inch, y, f"${subtotal:,.2f}")
    c.drawRightString(7.1 * inch, y, f"${total_viaticos:,.2f}")
    importe = subtotal + total_viaticos
    c.drawRightString(7.6 * inch, y, f"${importe:,.2f}")
    y -= 0.3 * inch
    iva = importe * 0.16
    total = importe + iva
    # Caja de totales a la derecha
    c.setFont("Helvetica-Bold", 11)
    c.drawString(6.0 * inch, y, "IMPORTE:")
    c.drawRightString(7.6 * inch, y, f"${importe:,.2f}")
    y -= 0.25 * inch
    c.drawString(6.0 * inch, y, "IVA:")
    c.drawRightString(7.6 * inch, y, f"${iva:,.2f}")
    y -= 0.25 * inch
    c.drawString(6.0 * inch, y, "TOTAL:")
    c.drawRightString(7.6 * inch, y, f"${total:,.2f}")

    c.showPage()
    c.save()
    return filename
