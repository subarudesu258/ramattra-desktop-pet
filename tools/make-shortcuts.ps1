# Create the desktop shortcut and the "run at login" entry for Ramattra Pet.
# Called by install-to-pc.bat (kept in its own file so cmd quoting cannot break it).

param(
    [Parameter(Mandatory = $true)][string]$Pythonw,
    [Parameter(Mandatory = $true)][string]$AppDir,
    [string]$Name = "Ramattra Pet"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Pythonw)) { throw "pythonw not found: $Pythonw" }
if (-not (Test-Path $AppDir)) { throw "app dir not found: $AppDir" }

$desktop = [Environment]::GetFolderPath("Desktop")
$startup = [Environment]::GetFolderPath("Startup")

$shell = New-Object -ComObject WScript.Shell

function New-PetShortcut {
    param([string]$Path)
    $link = $shell.CreateShortcut($Path)
    $link.TargetPath = $Pythonw
    $link.Arguments = "-m ramattra_pet"
    $link.WorkingDirectory = $AppDir
    $link.IconLocation = "$Pythonw,0"
    $link.Description = "Ramattra desktop pet"
    $link.WindowStyle = 7   # minimised: the Tk window is borderless anyway
    $link.Save()
    Write-Output ("created: " + $Path)
}

New-PetShortcut -Path (Join-Path $desktop "$Name.lnk")
New-PetShortcut -Path (Join-Path $startup "$Name.lnk")
