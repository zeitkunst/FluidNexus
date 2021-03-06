; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Fluid Nexus"
#define MyAppNameUnderscores "Fluid_Nexus"
#define MyAppVersion "0.2.6"
#define MyAppURL "http://fluidnexus.net"
#define MyAppExeName "fluid-nexus.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{ECF9D701-538C-4B3D-8B5C-ACBED296F45B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\LICENSE
InfoBeforeFile=C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\README.rst
OutputBaseFilename={#MyAppNameUnderscores}_{#MyAppVersion}_Setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\dist\fluid-nexus.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\dist\share\*"; DestDir: "{app}\share"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\dist\Microsoft.VC90.CRT\*.*"; DestDir: "{app}\Microsoft.VC90.CRT"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Documents and Settings\Nicholas Knouf\Development\Android\FluidNexus\dist\Microsoft.VC90.CRT\*.*"; DestDir: "{app}\lib\Microsoft.VC90.CRT"; Flags: ignoreversion recursesubdirs createallsubdirs

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, "&", "&&")}}"; Flags: nowait postinstall skipifsilent
