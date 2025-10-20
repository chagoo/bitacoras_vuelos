from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bitácoras de Vuelos - Mantenimiento Aéreo")
        self.resize(1100, 700)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QHBoxLayout(central)

        # Sidebar
        self.menu_list = QtWidgets.QListWidget()
        self.menu_list.addItems(["Clientes", "Insumos", "Aeronaves", "Vuelos", "Catálogos", "Reportes", "Configuración"]) 
        self.menu_list.setFixedWidth(180)
        layout.addWidget(self.menu_list)

        # Stacked pages
        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.page_clients = self._build_clients_page()
        self.page_supplies = self._build_supplies_page()
        self.page_aircraft = self._build_aircraft_page()
        self.page_flights = self._build_flights_page()
        self.page_catalogs = self._build_catalogs_page()
        self.page_reports = self._build_reports_page()
        self.page_settings = self._build_settings_page()

        self.stack.addWidget(self.page_clients)
        self.stack.addWidget(self.page_supplies)
        self.stack.addWidget(self.page_aircraft)
        self.stack.addWidget(self.page_flights)
        self.stack.addWidget(self.page_catalogs)
        self.stack.addWidget(self.page_reports)
        self.stack.addWidget(self.page_settings)

        self.menu_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.menu_list.setCurrentRow(0)

    def _build_clients_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        header = QtWidgets.QHBoxLayout()
        self.client_name = QtWidgets.QLineEdit(); self.client_name.setPlaceholderText("Nombre del cliente")
        self.client_add_btn = QtWidgets.QPushButton("Agregar")
        self.client_update_btn = QtWidgets.QPushButton("Actualizar")
        header.addWidget(self.client_name)
        header.addWidget(self.client_add_btn)
        header.addWidget(self.client_update_btn)
        v.addLayout(header)
        self.clients_table = QtWidgets.QTableWidget(0, 2)
        self.clients_table.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.clients_table.horizontalHeader().setStretchLastSection(True)
        self.clients_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.clients_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        v.addWidget(self.clients_table)
        return w

    def _build_supplies_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        header = QtWidgets.QHBoxLayout()
        self.supply_name = QtWidgets.QLineEdit(); self.supply_name.setPlaceholderText("Nombre del insumo")
        self.supply_unit = QtWidgets.QLineEdit(); self.supply_unit.setPlaceholderText("Unidad")
        self.supply_cpu = QtWidgets.QDoubleSpinBox(); self.supply_cpu.setPrefix("$ "); self.supply_cpu.setMaximum(1_000_000)
        self.supply_add_btn = QtWidgets.QPushButton("Agregar")
        self.supply_update_btn = QtWidgets.QPushButton("Actualizar")
        for wdg in (self.supply_name, self.supply_unit, self.supply_cpu, self.supply_add_btn):
            header.addWidget(wdg)
        header.addWidget(self.supply_update_btn)
        v.addLayout(header)
        self.supplies_table = QtWidgets.QTableWidget(0, 4)
        self.supplies_table.setHorizontalHeaderLabels(["ID", "Nombre", "Unidad", "Costo/U"]) 
        self.supplies_table.horizontalHeader().setStretchLastSection(True)
        self.supplies_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.supplies_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        v.addWidget(self.supplies_table)
        return w

    def _build_aircraft_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        header = QtWidgets.QHBoxLayout()
        self.ac_reg = QtWidgets.QLineEdit(); self.ac_reg.setPlaceholderText("Matrícula (ej. XA-JMA)")
        self.ac_model = QtWidgets.QLineEdit(); self.ac_model.setPlaceholderText("Modelo")
        self.ac_add_btn = QtWidgets.QPushButton("Agregar")
        self.ac_update_btn = QtWidgets.QPushButton("Actualizar")
        header.addWidget(self.ac_reg)
        header.addWidget(self.ac_model)
        header.addWidget(self.ac_add_btn)
        header.addWidget(self.ac_update_btn)
        v.addLayout(header)
        self.aircraft_table = QtWidgets.QTableWidget(0, 3)
        self.aircraft_table.setHorizontalHeaderLabels(["ID", "Matrícula", "Modelo"])
        self.aircraft_table.horizontalHeader().setStretchLastSection(True)
        self.aircraft_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.aircraft_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        v.addWidget(self.aircraft_table)
        return w

    def _build_flights_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        form = QtWidgets.QFormLayout()
        self.flight_date = QtWidgets.QDateEdit(); self.flight_date.setCalendarPopup(True); self.flight_date.setDate(QtCore.QDate.currentDate())
        self.flight_aircraft = QtWidgets.QComboBox()
        self.flight_client = QtWidgets.QComboBox(); self.flight_client.setEditable(True)
        self.flight_pilot = QtWidgets.QLineEdit()
        self.flight_origin = QtWidgets.QLineEdit(); self.flight_origin.setMaxLength(5)
        self.flight_destination = QtWidgets.QLineEdit(); self.flight_destination.setMaxLength(5)
        # Service type from catalog only
        self.flight_service_type_ref = QtWidgets.QComboBox()
        self.flight_mechanic = QtWidgets.QComboBox(); self.flight_mechanic.setEditable(True)
        self.flight_concept = QtWidgets.QComboBox(); self.flight_concept.setEditable(True)
        self.flight_service_time = QtWidgets.QTimeEdit(); self.flight_service_time.setDisplayFormat("hh:mm AP")
        self.flight_minutes = QtWidgets.QSpinBox(); self.flight_minutes.setMaximum(10_000)
        self.flight_landings = QtWidgets.QSpinBox(); self.flight_landings.setMaximum(100)
        self.flight_notes = QtWidgets.QTextEdit(); self.flight_notes.setPlaceholderText("Observaciones / Notas")
        form.addRow("Fecha:", self.flight_date)
        form.addRow("Aeronave:", self.flight_aircraft)
        form.addRow("Cliente:", self.flight_client)
        form.addRow("Piloto:", self.flight_pilot)
        form.addRow("Origen:", self.flight_origin)
        form.addRow("Destino:", self.flight_destination)
        form.addRow("Tipo Servicio (Cat):", self.flight_service_type_ref)
        form.addRow("Mecánico:", self.flight_mechanic)
        form.addRow("Concepto:", self.flight_concept)
        form.addRow("Hora de servicio:", self.flight_service_time)
        form.addRow("Minutos:", self.flight_minutes)
        form.addRow("Aterrizajes:", self.flight_landings)
        form.addRow("Observaciones:", self.flight_notes)
        v.addLayout(form)
        self.flight_add_btn = QtWidgets.QPushButton("Guardar vuelo")
        v.addWidget(self.flight_add_btn)
        self.flights_table = QtWidgets.QTableWidget(0, 8)
        self.flights_table.setHorizontalHeaderLabels(["ID", "Fecha", "Matrícula", "Cliente", "Piloto", "Origen", "Destino", "Minutos"]) 
        self.flights_table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.flights_table)

        # Panel para asociar insumos al vuelo seleccionado
        gb = QtWidgets.QGroupBox("Asociar insumo al vuelo seleccionado")
        hb = QtWidgets.QHBoxLayout(gb)
        self.flight_supply_cb = QtWidgets.QComboBox()
        self.flight_supply_qty = QtWidgets.QDoubleSpinBox(); self.flight_supply_qty.setDecimals(2); self.flight_supply_qty.setMaximum(1_000_000)
        self.flight_supply_price = QtWidgets.QDoubleSpinBox(); self.flight_supply_price.setDecimals(2); self.flight_supply_price.setPrefix("$ "); self.flight_supply_price.setMaximum(1_000_000)
        self.flight_supply_viaticos = QtWidgets.QDoubleSpinBox(); self.flight_supply_viaticos.setDecimals(2); self.flight_supply_viaticos.setPrefix("$ "); self.flight_supply_viaticos.setMaximum(1_000_000)
        self.flight_supply_add_btn = QtWidgets.QPushButton("Agregar insumo al vuelo")
        for wdg in (
            QtWidgets.QLabel("Insumo:"), self.flight_supply_cb,
            QtWidgets.QLabel("Cant.:") , self.flight_supply_qty,
            QtWidgets.QLabel("Precio:"), self.flight_supply_price,
            QtWidgets.QLabel("Viáticos:"), self.flight_supply_viaticos,
            self.flight_supply_add_btn,
        ):
            hb.addWidget(wdg)
        v.addWidget(gb)
        return w

    def _build_catalogs_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs)

        # Service Types
        st = QtWidgets.QWidget(); stv = QtWidgets.QVBoxLayout(st)
        row = QtWidgets.QHBoxLayout();
        self.cat_st_name = QtWidgets.QLineEdit(); self.cat_st_name.setPlaceholderText("Nuevo tipo de servicio")
        self.cat_st_add = QtWidgets.QPushButton("Agregar")
        self.cat_st_update = QtWidgets.QPushButton("Actualizar")
        row.addWidget(self.cat_st_name); row.addWidget(self.cat_st_add); row.addWidget(self.cat_st_update)
        stv.addLayout(row)
        self.cat_st_table = QtWidgets.QTableWidget(0, 2); self.cat_st_table.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.cat_st_table.horizontalHeader().setStretchLastSection(True)
        self.cat_st_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cat_st_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        stv.addWidget(self.cat_st_table)
        tabs.addTab(st, "Tipos de Servicio")

        # Mechanics
        mech = QtWidgets.QWidget(); mv = QtWidgets.QVBoxLayout(mech)
        row = QtWidgets.QHBoxLayout();
        self.cat_mech_name = QtWidgets.QLineEdit(); self.cat_mech_name.setPlaceholderText("Nombre del mecánico")
        self.cat_mech_add = QtWidgets.QPushButton("Agregar")
        self.cat_mech_update = QtWidgets.QPushButton("Actualizar")
        row.addWidget(self.cat_mech_name); row.addWidget(self.cat_mech_add); row.addWidget(self.cat_mech_update)
        mv.addLayout(row)
        self.cat_mech_table = QtWidgets.QTableWidget(0, 2); self.cat_mech_table.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.cat_mech_table.horizontalHeader().setStretchLastSection(True)
        self.cat_mech_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cat_mech_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        mv.addWidget(self.cat_mech_table)
        tabs.addTab(mech, "Mecánicos")

        # Concepts
        con = QtWidgets.QWidget(); cv = QtWidgets.QVBoxLayout(con)
        row = QtWidgets.QHBoxLayout();
        self.cat_con_name = QtWidgets.QLineEdit(); self.cat_con_name.setPlaceholderText("Nombre del concepto")
        self.cat_con_add = QtWidgets.QPushButton("Agregar")
        self.cat_con_update = QtWidgets.QPushButton("Actualizar")
        row.addWidget(self.cat_con_name); row.addWidget(self.cat_con_add); row.addWidget(self.cat_con_update)
        cv.addLayout(row)
        self.cat_con_table = QtWidgets.QTableWidget(0, 2); self.cat_con_table.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.cat_con_table.horizontalHeader().setStretchLastSection(True)
        self.cat_con_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cat_con_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        cv.addWidget(self.cat_con_table)
        tabs.addTab(con, "Conceptos")
        return w

    def _build_reports_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        row = QtWidgets.QHBoxLayout()
        self.report_start = QtWidgets.QDateEdit(); self.report_start.setCalendarPopup(True); self.report_start.setDate(QtCore.QDate.currentDate().addMonths(-1))
        self.report_end = QtWidgets.QDateEdit(); self.report_end.setCalendarPopup(True); self.report_end.setDate(QtCore.QDate.currentDate())
        self.report_aircraft = QtWidgets.QComboBox()
        self.report_client = QtWidgets.QComboBox(); self.report_client.setEditable(True)
        self.report_btn = QtWidgets.QPushButton("Resumen de Vuelos (PDF)")
        self.report_prepost_btn = QtWidgets.QPushButton("Bitácora PRE/POST (PDF)")
        self.report_consumibles_btn = QtWidgets.QPushButton("Consumibles y Servicios (PDF)")
        self.report_preview_btn = QtWidgets.QPushButton("Ver en tabla")
        for wdg in (self.report_start, self.report_end, self.report_aircraft, self.report_client, self.report_preview_btn, self.report_btn, self.report_prepost_btn, self.report_consumibles_btn):
            row.addWidget(wdg)
        v.addLayout(row)
        self.report_status = QtWidgets.QLabel("Seleccione periodo y genere el reporte.")
        v.addWidget(self.report_status)
        # preview table
        self.report_table = QtWidgets.QTableWidget(0, 11)
        self.report_table.setHorizontalHeaderLabels(["Fecha", "Matrícula", "Cliente", "Tipo Serv.", "Mecánico", "Concepto", "Hora", "Origen", "Destino", "Minutos", "Aterrizajes"])
        self.report_table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.report_table)
        return w

    def _build_settings_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        form = QtWidgets.QFormLayout()
        self.cfg_name = QtWidgets.QLineEdit()
        self.cfg_address = QtWidgets.QTextEdit()
        self.cfg_phone = QtWidgets.QLineEdit()
        self.cfg_email = QtWidgets.QLineEdit()
        self.cfg_rfc = QtWidgets.QLineEdit()
        self.cfg_afac = QtWidgets.QLineEdit()
        self.cfg_logo = QtWidgets.QLineEdit(); self.cfg_logo.setPlaceholderText("Ruta de imagen (PNG/JPG)")
        self.cfg_logo_btn = QtWidgets.QPushButton("Seleccionar logo…")
        logo_row = QtWidgets.QHBoxLayout(); logo_row.addWidget(self.cfg_logo); logo_row.addWidget(self.cfg_logo_btn)
        form.addRow("Nombre empresa:", self.cfg_name)
        form.addRow("Dirección:", self.cfg_address)
        form.addRow("Teléfono:", self.cfg_phone)
        form.addRow("Email:", self.cfg_email)
        form.addRow("RFC:", self.cfg_rfc)
        form.addRow("AFAC No.:", self.cfg_afac)
        form.addRow("Logo:", logo_row)
        v.addLayout(form)
        self.cfg_save_btn = QtWidgets.QPushButton("Guardar configuración")
        v.addWidget(self.cfg_save_btn)
        v.addStretch(1)
        return w
