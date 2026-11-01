[Setup]
AppName=JoyToy
AppVersion=1.0
AppPublisher=off chartz
DefaultDirName={autopf}\JoyToy
DefaultGroupName=JoyToy
OutputDir=.\Output
OutputBaseFilename=JoyToy_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=server_icon.ico
PrivilegesRequired=admin

[Files]
Source: "dist\JoyToy.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ViGEmBusSetup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\JoyToy"; Filename: "{app}\JoyToy.exe"; IconFilename: "{app}\JoyToy.exe"
Name: "{autodesktop}\JoyToy"; Filename: "{app}\JoyToy.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"

[Run]
Filename: "{tmp}\ViGEmBusSetup.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing ViGEmBus Controller Driver (Required)..."; Flags: waituntilterminated
Filename: "{app}\JoyToy.exe"; Description: "Launch JoyToy"; Flags: nowait postinstall skipifsilent