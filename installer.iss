[Setup]
AppName=NIFRAP 2.0
AppVersion=2.0.0
AppPublisher=NIFRAP
DefaultDirName={autopf}\NIFRAP
DefaultGroupName=NIFRAP
OutputDir=dist
OutputBaseFilename=NIFRAP_2.0_Setup
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\NIFRAP_2.0\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NIFRAP 2.0"; Filename: "{app}\NIFRAP_2.0.exe"
Name: "{group}\Uninstall NIFRAP 2.0"; Filename: "{uninstallexe}"
Name: "{autodesktop}\NIFRAP 2.0"; Filename: "{app}\NIFRAP_2.0.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\NIFRAP_2.0.exe"; Description: "{cm:LaunchProgram,NIFRAP 2.0}"; Flags: nowait postinstall skipifsilent
