from __future__ import annotations

import sys
from datetime import date, time

from PySide6 import QtWidgets, QtCore
from sqlalchemy import exc as sa_exc

from app.db import get_session
from app.models import Aircraft, Client
from app.repository import (
    add_aircraft,
    add_client,
    add_flight,
    add_flight_supply,
    init_db,
    list_aircraft,
    list_clients,
    list_flights_in_range,
    list_supplies,
    add_supply,
    list_mechanics,
    list_service_types,
    list_concepts,
    add_mechanic,
    add_service_type,
    add_concept,
)
from app.reporting import (
    generate_flights_summary_pdf,
    generate_bitacora_pre_post_pdf,
    generate_consumibles_servicios_pdf,
)
from app.ui_main import MainWindow
from app.company_config import CompanyConfig, load_company_config, save_company_config


class Controller:
    def __init__(self, window: MainWindow):
        self.w = window
        self.company = load_company_config()
        self._current_flight_id: int | None = None
        init_db()
        self._wire()
        self._refresh_all()

    def _wire(self) -> None:
        self.w.client_add_btn.clicked.connect(self._on_add_client)
        self.w.client_name.returnPressed.connect(self._on_add_client)
        # Edit buttons
        if hasattr(self.w, 'client_update_btn'):
            self.w.client_update_btn.clicked.connect(self._on_update_client)
        self.w.supply_add_btn.clicked.connect(self._on_add_supply)
        if hasattr(self.w, 'supply_update_btn'):
            self.w.supply_update_btn.clicked.connect(self._on_update_supply)
        self.w.ac_add_btn.clicked.connect(self._on_add_aircraft)
        if hasattr(self.w, 'ac_update_btn'):
            self.w.ac_update_btn.clicked.connect(self._on_update_aircraft)
        self.w.flight_add_btn.clicked.connect(self._on_add_flight)
        self.w.flight_supply_add_btn.clicked.connect(self._on_add_flight_supply)
        # Load flight form on table selection
        self.w.flights_table.itemSelectionChanged.connect(self._on_flight_row_selected)
        self.w.report_btn.clicked.connect(self._on_generate_report)
        self.w.report_prepost_btn.clicked.connect(self._on_generate_report_prepost)
        self.w.report_consumibles_btn.clicked.connect(self._on_generate_report_consumibles)
        if hasattr(self.w, 'report_preview_btn'):
            self.w.report_preview_btn.clicked.connect(self._on_preview_report_table)
        self.w.cfg_logo_btn.clicked.connect(self._on_pick_logo)
        self.w.cfg_save_btn.clicked.connect(self._on_save_company)
        # Catalogs buttons (if exist)
        if hasattr(self.w, 'cat_st_add'):
            self.w.cat_st_add.clicked.connect(self._on_add_service_type)
        if hasattr(self.w, 'cat_st_update'):
            self.w.cat_st_update.clicked.connect(self._on_update_service_type)
        if hasattr(self.w, 'cat_mech_add'):
            self.w.cat_mech_add.clicked.connect(self._on_add_mechanic)
        if hasattr(self.w, 'cat_mech_update'):
            self.w.cat_mech_update.clicked.connect(self._on_update_mechanic)
        if hasattr(self.w, 'cat_con_add'):
            self.w.cat_con_add.clicked.connect(self._on_add_concept)
        if hasattr(self.w, 'cat_con_update'):
            self.w.cat_con_update.clicked.connect(self._on_update_concept)

    def _refresh_all(self) -> None:
        self._load_clients()
        self._load_supplies()
        self._load_aircraft()
        self._load_flights_table()
        self._load_combo_boxes()
        self._load_company_to_form()
        self._load_catalogs()

    def _load_clients(self) -> None:
        with get_session() as s:
            clients = list_clients(s)
        t = self.w.clients_table
        t.setRowCount(0)
        for c in clients:
            row = t.rowCount(); t.insertRow(row)
            t.setItem(row, 0, QtWidgets.QTableWidgetItem(str(c.id)))
            t.setItem(row, 1, QtWidgets.QTableWidgetItem(c.name))

    def _load_supplies(self) -> None:
        with get_session() as s:
            supplies = list_supplies(s)
        t = self.w.supplies_table
        t.setRowCount(0)
        for sup in supplies:
            row = t.rowCount(); t.insertRow(row)
            t.setItem(row, 0, QtWidgets.QTableWidgetItem(str(sup.id)))
            t.setItem(row, 1, QtWidgets.QTableWidgetItem(sup.name))
            t.setItem(row, 2, QtWidgets.QTableWidgetItem(sup.unit))
            t.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{float(sup.cost_per_unit):.2f}"))

    def _load_aircraft(self) -> None:
        with get_session() as s:
            aircraft = list_aircraft(s)
        t = self.w.aircraft_table
        t.setRowCount(0)
        for a in aircraft:
            row = t.rowCount(); t.insertRow(row)
            t.setItem(row, 0, QtWidgets.QTableWidgetItem(str(a.id)))
            t.setItem(row, 1, QtWidgets.QTableWidgetItem(a.registration))
            t.setItem(row, 2, QtWidgets.QTableWidgetItem(a.model or ""))

    def _load_flights_table(self) -> None:
        # Load this month flights as a simple default
        today = date.today()
        start = date(today.year, today.month, 1)
        end = date(today.year + (1 if today.month == 12 else 0), 1 if today.month == 12 else today.month + 1, 1)
        with get_session() as s:
            flights = list_flights_in_range(s, start, end)
        t = self.w.flights_table
        t.setRowCount(0)
        for f in flights:
            row = t.rowCount(); t.insertRow(row)
            t.setItem(row, 0, QtWidgets.QTableWidgetItem(str(f.id)))
            t.setItem(row, 1, QtWidgets.QTableWidgetItem(f.flight_date.isoformat()))
            t.setItem(row, 2, QtWidgets.QTableWidgetItem(f.aircraft.registration if f.aircraft else ""))
            t.setItem(row, 3, QtWidgets.QTableWidgetItem(f.client.name if f.client else ""))
            t.setItem(row, 4, QtWidgets.QTableWidgetItem(f.pilot))
            t.setItem(row, 5, QtWidgets.QTableWidgetItem(f.origin))
            t.setItem(row, 6, QtWidgets.QTableWidgetItem(f.destination))
            t.setItem(row, 7, QtWidgets.QTableWidgetItem(str(f.flight_minutes)))
        # when reloading, clear selection and reset editing state
        self._current_flight_id = None
        t.clearSelection()
        self._set_flight_form_mode_insert()

    def _load_combo_boxes(self) -> None:
        with get_session() as s:
            aircraft = list_aircraft(s)
            clients = list_clients(s)
            supplies = list_supplies(s)
            mechanics = list_mechanics(s)
            service_types = list_service_types(s)
            concepts = list_concepts(s)
        self.w.flight_aircraft.clear()
        for a in aircraft:
            self.w.flight_aircraft.addItem(a.registration, a.id)
        self.w.flight_client.clear()
        self.w.flight_client.addItem("(Sin cliente)", None)
        for c in clients:
            self.w.flight_client.addItem(c.name, c.id)
        # supplies
        self.w.flight_supply_cb.clear()
        for s in supplies:
            self.w.flight_supply_cb.addItem(s.name, s.id)
        # report filters combos
        if hasattr(self.w, 'report_aircraft'):
            self.w.report_aircraft.clear(); self.w.report_aircraft.addItem("(Todas)")
            for a in aircraft:
                self.w.report_aircraft.addItem(a.registration)
        if hasattr(self.w, 'report_client'):
            self.w.report_client.clear(); self.w.report_client.addItem("(Todos)")
            for c in clients:
                self.w.report_client.addItem(c.name)
        # catalogs in flight form (if present)
        if hasattr(self.w, 'flight_mechanic'):
            self.w.flight_mechanic.clear()
            self.w.flight_mechanic.addItem("(Ninguno)", None)
            for m in mechanics:
                self.w.flight_mechanic.addItem(m.name, m.id)
        if hasattr(self.w, 'flight_service_type_ref'):
            self.w.flight_service_type_ref.clear()
            self.w.flight_service_type_ref.addItem("(Ninguno)", None)
            for st in service_types:
                self.w.flight_service_type_ref.addItem(st.name, st.id)
        if hasattr(self.w, 'flight_concept'):
            self.w.flight_concept.clear()
            self.w.flight_concept.addItem("(Ninguno)", None)
            for cpt in concepts:
                self.w.flight_concept.addItem(cpt.name, cpt.id)

    def _load_catalogs(self) -> None:
        if not hasattr(self.w, 'cat_st_table'):
            return
        with get_session() as s:
            sts = list_service_types(s)
            mechs = list_mechanics(s)
            cons = list_concepts(s)
        # service types table
        t = self.w.cat_st_table; t.setRowCount(0)
        for st in sts:
            r = t.rowCount(); t.insertRow(r)
            t.setItem(r, 0, QtWidgets.QTableWidgetItem(str(st.id)))
            t.setItem(r, 1, QtWidgets.QTableWidgetItem(st.name))
        # mechanics
        t = self.w.cat_mech_table; t.setRowCount(0)
        for m in mechs:
            r = t.rowCount(); t.insertRow(r)
            t.setItem(r, 0, QtWidgets.QTableWidgetItem(str(m.id)))
            t.setItem(r, 1, QtWidgets.QTableWidgetItem(m.name))
        # concepts
        t = self.w.cat_con_table; t.setRowCount(0)
        for c in cons:
            r = t.rowCount(); t.insertRow(r)
            t.setItem(r, 0, QtWidgets.QTableWidgetItem(str(c.id)))
            t.setItem(r, 1, QtWidgets.QTableWidgetItem(c.name))

    def _load_company_to_form(self) -> None:
        self.w.cfg_name.setText(self.company.name)
        self.w.cfg_address.setPlainText(self.company.address)
        self.w.cfg_phone.setText(self.company.phone)
        self.w.cfg_email.setText(self.company.email)
        self.w.cfg_rfc.setText(self.company.rfc)
        self.w.cfg_afac.setText(self.company.afac_no)
        self.w.cfg_logo.setText(self.company.logo_path)

    def _on_pick_logo(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.w, "Seleccionar logo", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.w.cfg_logo.setText(path)

    def _on_save_company(self):
        self.company.name = self.w.cfg_name.text().strip()
        self.company.address = self.w.cfg_address.toPlainText().strip()
        self.company.phone = self.w.cfg_phone.text().strip()
        self.company.email = self.w.cfg_email.text().strip()
        self.company.rfc = self.w.cfg_rfc.text().strip()
        self.company.afac_no = self.w.cfg_afac.text().strip()
        self.company.logo_path = self.w.cfg_logo.text().strip()
        save_company_config(self.company)
        QtWidgets.QMessageBox.information(self.w, "Configuración", "Datos de empresa guardados.")

    # Slots
    def _on_add_client(self):
        name = self.w.client_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del cliente")
            return
        try:
            with get_session() as s:
                add_client(s, name=name)
        except sa_exc.IntegrityError:
            QtWidgets.QMessageBox.warning(self.w, "Duplicado", "Ya existe un cliente con ese nombre")
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo guardar el cliente.\n{e}")
            return
        self.w.client_name.clear()
        self._load_clients()
        self._load_combo_boxes()
        QtWidgets.QMessageBox.information(self.w, "Cliente", "Cliente agregado correctamente")

    def _on_add_supply(self):
        name = self.w.supply_name.text().strip()
        unit = self.w.supply_unit.text().strip() or "unidad"
        cpu = float(self.w.supply_cpu.value())
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del insumo")
            return
        try:
            with get_session() as s:
                add_supply(s, name=name, unit=unit, cost_per_unit=cpu)
        except sa_exc.IntegrityError:
            QtWidgets.QMessageBox.warning(self.w, "Duplicado", "Ya existe un insumo con ese nombre")
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo guardar el insumo.\n{e}")
            return
        self.w.supply_name.clear(); self.w.supply_unit.clear(); self.w.supply_cpu.setValue(0)
        self._load_supplies()
        self._load_combo_boxes()

    def _on_add_aircraft(self):
        reg = self.w.ac_reg.text().strip()
        model = self.w.ac_model.text().strip() or None
        if not reg:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese la matrícula")
            return
        try:
            with get_session() as s:
                add_aircraft(s, registration=reg, model=model)
        except sa_exc.IntegrityError:
            QtWidgets.QMessageBox.warning(self.w, "Duplicado", "Ya existe una aeronave con esa matrícula")
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo guardar la aeronave.\n{e}")
            return
        self.w.ac_reg.clear(); self.w.ac_model.clear()
        self._load_aircraft()
        self._load_combo_boxes()

    def _on_add_flight(self):
        dt = self.w.flight_date.date().toPython()
        ac_id = self.w.flight_aircraft.currentData()
        client_id = self.w.flight_client.currentData()
        pilot = self.w.flight_pilot.text().strip() or "N/A"
        origin = self.w.flight_origin.text().strip().upper() or "N/A"
        dest = self.w.flight_destination.text().strip().upper() or "N/A"
        qtime = self.w.flight_service_time.time()
        service_time = time(hour=qtime.hour(), minute=qtime.minute()) if qtime.isValid() else None
        notes = self.w.flight_notes.toPlainText().strip() or None
        minutes = int(self.w.flight_minutes.value())
        landings = int(self.w.flight_landings.value())
        if not ac_id:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Seleccione una aeronave")
            return
        try:
            with get_session() as s:
                if self._current_flight_id:
                    obj = s.get(__import__('app.models', fromlist=['FlightLog']).FlightLog, self._current_flight_id)
                    if obj:
                        obj.flight_date = dt
                        obj.aircraft_id = ac_id
                        obj.client_id = client_id
                        obj.pilot = pilot
                        obj.copilot = None
                        obj.origin = origin
                        obj.destination = dest
                        obj.service_type = None
                        obj.service_time = service_time
                        obj.mechanic_id = (self.w.flight_mechanic.currentData() if hasattr(self.w, 'flight_mechanic') else None)
                        obj.service_type_id = (self.w.flight_service_type_ref.currentData() if hasattr(self.w, 'flight_service_type_ref') else None)
                        obj.concept_id = (self.w.flight_concept.currentData() if hasattr(self.w, 'flight_concept') else None)
                        obj.notes = notes
                        obj.flight_minutes = minutes
                        obj.landings = landings
                else:
                    add_flight(
                        s,
                        flight_date=dt,
                        aircraft_id=ac_id,
                        client_id=client_id,
                        pilot=pilot,
                        copilot=None,
                        origin=origin,
                        destination=dest,
                        service_type=None,
                        service_time=service_time,
                        mechanic_id=(self.w.flight_mechanic.currentData() if hasattr(self.w, 'flight_mechanic') else None),
                        service_type_id=(self.w.flight_service_type_ref.currentData() if hasattr(self.w, 'flight_service_type_ref') else None),
                        concept_id=(self.w.flight_concept.currentData() if hasattr(self.w, 'flight_concept') else None),
                        notes=notes,
                        flight_minutes=minutes,
                        landings=landings,
                    )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo guardar el vuelo.\n{e}")
            return
        self._load_flights_table()
        self._load_combo_boxes()

    def _on_flight_row_selected(self):
        row = self.w.flights_table.currentRow()
        if row < 0:
            self._current_flight_id = None
            self._set_flight_form_mode_insert()
            return
        fid_item = self.w.flights_table.item(row, 0)
        if not fid_item:
            return
        fid = int(fid_item.text())
        # Load the latest object state from DB
        from app.models import FlightLog
        with get_session() as s:
            obj = s.get(FlightLog, fid)
        if not obj:
            return
        self._current_flight_id = fid
        # Populate form
        self.w.flight_date.setDate(obj.flight_date)
        # set current aircraft/client by id
        self._set_combo_by_data(self.w.flight_aircraft, obj.aircraft_id)
        self._set_combo_by_data(self.w.flight_client, obj.client_id)
        self.w.flight_pilot.setText(obj.pilot or "")
        self.w.flight_origin.setText(obj.origin or "")
        self.w.flight_destination.setText(obj.destination or "")
        # service type legacy field removed; use catalog only
        if obj.service_time:
            self.w.flight_service_time.setTime(obj.service_time)
        else:
            self.w.flight_service_time.setTime(QtCore.QTime(0,0))
        self._set_combo_by_data(getattr(self.w, 'flight_mechanic', None), getattr(obj, 'mechanic_id', None))
        self._set_combo_by_data(getattr(self.w, 'flight_service_type_ref', None), getattr(obj, 'service_type_id', None))
        self._set_combo_by_data(getattr(self.w, 'flight_concept', None), getattr(obj, 'concept_id', None))
        self.w.flight_minutes.setValue(int(obj.flight_minutes or 0))
        self.w.flight_landings.setValue(int(obj.landings or 0))
        self.w.flight_notes.setPlainText(obj.notes or "")
        self._set_flight_form_mode_update()

    def _set_combo_by_data(self, combo, value):
        if combo is None:
            return
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def _set_flight_form_mode_insert(self):
        self.w.flight_add_btn.setText("Guardar vuelo")

    def _set_flight_form_mode_update(self):
        self.w.flight_add_btn.setText("Actualizar vuelo")

    def _on_preview_report_table(self):
        start = self.w.report_start.date().toPython()
        end = self.w.report_end.date().toPython()
        with get_session() as s:
            flights = list_flights_in_range(s, start, end)
        ac_text = self.w.report_aircraft.currentText() if hasattr(self.w, 'report_aircraft') else "(Todas)"
        cl_text = self.w.report_client.currentText() if hasattr(self.w, 'report_client') else "(Todos)"
        if ac_text and ac_text != "(Todas)":
            flights = [f for f in flights if f.aircraft and f.aircraft.registration == ac_text]
        if cl_text and cl_text != "(Todos)":
            flights = [f for f in flights if f.client and f.client.name == cl_text]
        t = self.w.report_table
        t.setRowCount(0)
        for f in flights:
            r = t.rowCount(); t.insertRow(r)
            t.setItem(r, 0, QtWidgets.QTableWidgetItem(f.flight_date.isoformat()))
            t.setItem(r, 1, QtWidgets.QTableWidgetItem(f.aircraft.registration if f.aircraft else ""))
            t.setItem(r, 2, QtWidgets.QTableWidgetItem(f.client.name if f.client else ""))
            st_label = f.service_type or (getattr(f, 'service_type_ref', None).name if getattr(f, 'service_type_ref', None) else "")
            t.setItem(r, 3, QtWidgets.QTableWidgetItem(st_label))
            t.setItem(r, 4, QtWidgets.QTableWidgetItem(getattr(f.mechanic, 'name', "")))
            t.setItem(r, 5, QtWidgets.QTableWidgetItem(getattr(f.concept, 'name', "")))
            t.setItem(r, 6, QtWidgets.QTableWidgetItem(f.service_time.strftime("%H:%M") if f.service_time else ""))
            t.setItem(r, 7, QtWidgets.QTableWidgetItem(f.origin or ""))
            t.setItem(r, 8, QtWidgets.QTableWidgetItem(f.destination or ""))
            t.setItem(r, 9, QtWidgets.QTableWidgetItem(str(f.flight_minutes)))
            t.setItem(r, 10, QtWidgets.QTableWidgetItem(str(f.landings)))

    # Catalog update handlers
    def _on_update_service_type(self):
        row = self.w.cat_st_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione un tipo de servicio")
            return
        sid = int(self.w.cat_st_table.item(row, 0).text())
        name = self.w.cat_st_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre")
            return
        from app.models import ServiceType
        try:
            with get_session() as s:
                obj = s.get(ServiceType, sid)
                if obj:
                    obj.name = name
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar.\n{e}")
            return
        self._load_catalogs(); self._load_combo_boxes()

    def _on_update_mechanic(self):
        row = self.w.cat_mech_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione un mecánico")
            return
        mid = int(self.w.cat_mech_table.item(row, 0).text())
        name = self.w.cat_mech_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre")
            return
        from app.models import Mechanic
        try:
            with get_session() as s:
                obj = s.get(Mechanic, mid)
                if obj:
                    obj.name = name
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar.\n{e}")
            return
        self._load_catalogs(); self._load_combo_boxes()

    def _on_update_concept(self):
        row = self.w.cat_con_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione un concepto")
            return
        cid = int(self.w.cat_con_table.item(row, 0).text())
        name = self.w.cat_con_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre")
            return
        from app.models import Concept
        try:
            with get_session() as s:
                obj = s.get(Concept, cid)
                if obj:
                    obj.name = name
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar.\n{e}")
            return
        self._load_catalogs(); self._load_combo_boxes()

    # Update handlers
    def _on_update_client(self):
        row = self.w.clients_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione un cliente en la tabla")
            return
        cid = int(self.w.clients_table.item(row, 0).text())
        name = self.w.client_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del cliente")
            return
        try:
            with get_session() as s:
                obj = s.get(Client, cid)
                if obj:
                    obj.name = name
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar el cliente.\n{e}")
            return
        self._load_clients(); self._load_combo_boxes()

    def _on_update_supply(self):
        row = self.w.supplies_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione un insumo en la tabla")
            return
        sid = int(self.w.supplies_table.item(row, 0).text())
        name = self.w.supply_name.text().strip()
        unit = self.w.supply_unit.text().strip() or "unidad"
        cpu = float(self.w.supply_cpu.value())
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del insumo")
            return
        try:
            with get_session() as s:
                obj = s.get(type(next(iter([]), None)) or __import__('app.models', fromlist=['Supply']).Supply, sid)
                # simpler: get and update via raw query
                from app.models import Supply as _Supply
                obj = s.get(_Supply, sid)
                if obj:
                    obj.name = name; obj.unit = unit; obj.cost_per_unit = cpu
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar el insumo.\n{e}")
            return
        self._load_supplies(); self._load_combo_boxes()

    def _on_update_aircraft(self):
        row = self.w.aircraft_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección", "Seleccione una aeronave en la tabla")
            return
        aid = int(self.w.aircraft_table.item(row, 0).text())
        reg = self.w.ac_reg.text().strip()
        model = self.w.ac_model.text().strip() or None
        if not reg:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese la matrícula")
            return
        try:
            with get_session() as s:
                obj = s.get(Aircraft, aid)
                if obj:
                    obj.registration = reg; obj.model = model
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo actualizar la aeronave.\n{e}")
            return
        self._load_aircraft(); self._load_combo_boxes()

    # Catalog add handlers
    def _on_add_service_type(self):
        name = self.w.cat_st_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el tipo de servicio")
            return
        try:
            with get_session() as s:
                add_service_type(s, name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo agregar el tipo de servicio.\n{e}")
            return
        self.w.cat_st_name.clear(); self._load_catalogs(); self._load_combo_boxes()

    def _on_add_mechanic(self):
        name = self.w.cat_mech_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del mecánico")
            return
        try:
            with get_session() as s:
                add_mechanic(s, name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo agregar el mecánico.\n{e}")
            return
        self.w.cat_mech_name.clear(); self._load_catalogs(); self._load_combo_boxes()

    def _on_add_concept(self):
        name = self.w.cat_con_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "Ingrese el nombre del concepto")
            return
        try:
            with get_session() as s:
                add_concept(s, name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo agregar el concepto.\n{e}")
            return
        self.w.cat_con_name.clear(); self._load_catalogs(); self._load_combo_boxes()

    def _on_add_flight_supply(self):
        # needs a selected flight row
        row = self.w.flights_table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self.w, "Selección requerida", "Seleccione un vuelo en la tabla")
            return
        flight_id = int(self.w.flights_table.item(row, 0).text())
        supply_id = self.w.flight_supply_cb.currentData()
        qty = float(self.w.flight_supply_qty.value())
        price = float(self.w.flight_supply_price.value())
        viaticos = float(self.w.flight_supply_viaticos.value())
        try:
            with get_session() as s:
                add_flight_supply(s, flight_id=flight_id, supply_id=supply_id, quantity=qty, unit_cost=price, viaticos=viaticos)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.w, "Error", f"No se pudo asociar el insumo.\n{e}")
            return
        QtWidgets.QMessageBox.information(self.w, "OK", "Insumo asociado al vuelo")

    def _on_generate_report(self):
        start = self.w.report_start.date().toPython()
        end = self.w.report_end.date().toPython()
        if start > end:
            QtWidgets.QMessageBox.warning(self.w, "Validación", "La fecha inicial debe ser <= a la final")
            return
        with get_session() as s:
            flights = list_flights_in_range(s, start, end)
        path = generate_flights_summary_pdf(flights, start, end)
        self.w.report_status.setText(f"Reporte generado: {path}")

    def _on_generate_report_prepost(self):
        # Use month/year from start date for the layout
        d = self.w.report_start.date().toPython()
        month, year = d.month, d.year
        client_name = self.w.report_client.currentText()
        if client_name == "(Todos)":
            client_name = ""
        matricula = self.w.report_aircraft.currentText()
        if matricula == "(Todas)":
            matricula = ""
        # Pull flights for the month
        start = date(year, month, 1)
        end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
        with get_session() as s:
            flights = list_flights_in_range(s, start, end)
        # Apply filters if provided
        if matricula:
            flights = [f for f in flights if f.aircraft and f.aircraft.registration == matricula]
        if client_name:
            flights = [f for f in flights if f.client and f.client.name == client_name]
        path = generate_bitacora_pre_post_pdf(flights, month, year, client_name, matricula)
        self.w.report_status.setText(f"Bitácora PRE/POST: {path}")

    def _on_generate_report_consumibles(self):
        d = self.w.report_start.date().toPython()
        month, year = d.month, d.year
        client_name = self.w.report_client.currentText()
        if client_name == "(Todos)":
            client_name = ""
        matricula = self.w.report_aircraft.currentText()
        if matricula == "(Todas)":
            matricula = ""
        start = date(year, month, 1)
        end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
        with get_session() as s:
            flights = list_flights_in_range(s, start, end)
        if matricula:
            flights = [f for f in flights if f.aircraft and f.aircraft.registration == matricula]
        if client_name:
            flights = [f for f in flights if f.client and f.client.name == client_name]
        path = generate_consumibles_servicios_pdf(flights, month, year, client_name, matricula)
        self.w.report_status.setText(f"Consumibles y Servicios: {path}")


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    # Keep a strong reference to the controller to prevent GC disconnecting signals
    w.controller = Controller(w)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
