# Bitácoras de Vuelos - Mantenimiento Aéreo

Aplicación de escritorio para capturar bitácoras post vuelo, administrar clientes e insumos, y generar reportes PDF. Funciona con SQLite y puede empaquetarse para instalar en otros equipos Windows.

## Requisitos

- Windows 10/11
- Python 3.10 o superior

## Instalación (desarrollo)

1. Crear y activar un entorno virtual
   
	PowerShell:
   
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

2. Instalar dependencias

	```powershell
	pip install -r requirements.txt
	```

3. Ejecutar la app

	```powershell
	python main.py
	```

La base de datos se crea automáticamente en `data/bitacoras.db`.

## Empaquetado para Windows (instalable)

Usaremos PyInstaller para generar un ejecutable autónomo.

1. Instalar PyInstaller

	```powershell
	pip install pyinstaller==6.6.0
	```

2. Generar ejecutable

	```powershell
	pyinstaller --noconfirm --onedir --windowed --name BitacorasVuelos ^
	  --add-data "data;data" --add-data "reports;reports" ^
	  main.py
	```

	Esto crea `dist/BitacorasVuelos/` con el `.exe`.

3. Opcional: crear un instalador MSI/EXE

	- Puede usar herramientas como Inno Setup o Wix Toolset para crear un instalador que copie `dist/BitacorasVuelos` a `C:\Program Files` y cree accesos directos.

## Funcionalidad

- Clientes: alta/baja básica y listado
- Insumos: alta y listado con costo por unidad
- Aeronaves: registrar matrícula y modelo
- Vuelos: captura básica (fecha, aeronave, cliente, piloto, ruta, minutos, aterrizajes)
- Reportes: PDF con resumen de vuelos por rango de fechas

## Próximos pasos sugeridos

- Validaciones y edición/eliminación de registros desde las tablas
- Cálculo de costos por vuelo con insumos utilizados
- Reporte detallado por cliente/aeronave
- Exportación/importación a Excel (pandas/openpyxl)
