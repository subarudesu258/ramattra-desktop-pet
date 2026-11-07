# Install Ramattra Pet for the current user (no admin required).
#
#   * copies the app to %LOCALAPPDATA%\Programs\RamattraPet\app
#   * locates a Python 3.10+ with tkinter
#   * writes a desktop shortcut and a "run at login" shortcut
#   * launches the pet
#
# Kept in PowerShell (not cmd) because path handling, COM shortcuts and error
# reporting are all less error-prone here. ASCII only: Windows PowerShell 5.1
# reads .ps1 as ANSI unless the file has a BOM.

param(
    [switch]$NoLaunch,
    [string]$Name = "Ramattra Pet"
)

$ErrorActionPreference = "Stop"

$here   = Split-Path -Parent $PSScriptRoot
$appDir = Join-Path $env:LOCALAPPDATA "Programs\RamattraPet"
$dest   = Join-Path $appDir "app"

Write-Host ""
Write-Host "  Ramattra Pet - installing for $env:USERNAME"
Write-Host "  target: $appDir"
Write-Host ""

# ---- 1. copy the app -------------------------------------------------------
New-Item -ItemType Directory -Path $dest -Force | Out-Null

$excludeDirs = @(".git", "_tmp_tests", "__pycache__", ".pytest_cache")
$excludeExt  = @(".pyc")

function Copy-Tree {
    param([string]$From, [string]$To)
    $stack = New-Object System.Collections.Stack
    $stack.Push("")
    while ($stack.Count -gt 0) {
        $rel = $stack.Pop()
        $srcDir = if ($rel) { Join-Path $From $rel } else { $From }
        $dstDir = if ($rel) { Join-Path $To $rel } else { $To }
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        foreach ($f in Get-ChildItem -LiteralPath $srcDir -File) {
            if ($excludeExt -contains $f.Extension) { continue }
            Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $dstDir $f.Name) -Force
        }
        foreach ($d in Get-ChildItem -LiteralPath $srcDir -Directory) {
            if ($excludeDirs -contains $d.Name) { continue }
            $child = if ($rel) { Join-Path $rel $d.Name } else { $d.Name }
            $stack.Push($child)
        }
    }
}

Copy-Tree -From $here -To $dest
Write-Host "  [ok] app copied to $dest"

# ---- 2. find pythonw -------------------------------------------------------
$candidates = @(
    (Join-Path $dest "python\pythonw.exe"),
    (Join-Path $appDir "python\pythonw.exe")
)
$onPath = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($onPath) { $candidates += $onPath.Source }
foreach ($root in @("$env:LOCALAPPDATA\Programs\Python", "$env:ProgramFiles\Python", "C:\Python3")) {
    if (Test-Path $root) {
        Get-ChildItem -Path $root -Directory -Filter "Python3*" -ErrorAction SilentlyContinue |
            ForEach-Object { $candidates += (Join-Path $_.FullName "pythonw.exe") }
    }
}
$launcher = Join-Path $env:LOCALAPPDATA "Programs\Python\Launcher\pyw.exe"

function Test-Python {
    # pythonw.exe is a GUI subsystem binary: "&" does not wait for it. Probe with
    # the console twin so the exit code is real, falling back to Start-Process.
    param([string]$W)
    $console = Join-Path (Split-Path -Parent $W) "python.exe"
    if (Test-Path -LiteralPath $console) {
        & $console -c "import tkinter" 2>$null
        return ($LASTEXITCODE -eq 0)
    }
    $p = Start-Process -FilePath $W -ArgumentList "-c", "import tkinter" -Wait -PassThru -WindowStyle Hidden
    return ($p.ExitCode -eq 0)
}

$pyw = $null
$checked = @()
foreach ($c in $candidates) {
    if (-not $c -or $checked -contains $c) { continue }
    $checked += $c
    if (-not (Test-Path -LiteralPath $c)) { continue }
    if (Test-Python -W $c) { $pyw = $c; break }
}

if (-not $pyw -and (Test-Path -LiteralPath $launcher)) {
    $consoleLauncher = Join-Path (Split-Path -Parent $launcher) "py.exe"
    if (Test-Path -LiteralPath $consoleLauncher) {
        & $consoleLauncher -3 -c "import tkinter" 2>$null
        if ($LASTEXITCODE -eq 0) { $pyw = $launcher }
    }
}

if (-not $pyw) {
    Write-Host "  [x] no usable Python 3.10+ with tkinter found."
    Write-Host ""
    Write-Host "      Install Python from https://www.python.org/downloads/"
    Write-Host "      (tick 'Add python.exe to PATH'), then run this again."
    Write-Host ""
    exit 1
}
Write-Host "  [ok] python: $pyw"

# ---- 3. shortcuts ----------------------------------------------------------
$shell = New-Object -ComObject WScript.Shell
$targets = @(
    (Join-Path ([Environment]::GetFolderPath("Desktop")) "$Name.lnk"),
    (Join-Path ([Environment]::GetFolderPath("Startup")) "$Name.lnk")
)
foreach ($path in $targets) {
    $link = $shell.CreateShortcut($path)
    $link.TargetPath = $pyw
    $link.Arguments = "-m ramattra_pet"
    $link.WorkingDirectory = $dest
    $link.IconLocation = "$pyw,0"
    $link.Description = "Ramattra desktop pet"
    $link.WindowStyle = 7
    $link.Save()
    Write-Host "  [ok] shortcut: $path"
}

# ---- 4. launch -------------------------------------------------------------
if (-not $NoLaunch) {
    Start-Process -FilePath $pyw -ArgumentList "-m", "ramattra_pet" -WorkingDirectory $dest
    Write-Host "  [ok] pet started"
}

Write-Host ""
Write-Host "  Done. Right-click the pet for the menu."
