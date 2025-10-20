; Inno Setup script for Bitácoras de Vuelos
; Adjust paths before building

[Setup]
AppName=Bitácoras de Vuelos
AppVersion=1.0.0
DefaultDirName={pf64}\BitacorasVuelos
DefaultGroupName=Bitácoras de Vuelos
OutputBaseFilename=BitacorasVuelos-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Update Source: to the output folder created by PyInstaller (dist/BitacorasVuelos)
Source: "..\dist\BitacorasVuelos\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Bitácoras de Vuelos"; Filename: "{app}\BitacorasVuelos.exe"
Name: "{commondesktop}\Bitácoras de Vuelos"; Filename: "{app}\BitacorasVuelos.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: unchecked
