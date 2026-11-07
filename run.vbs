' Launch the pet fully hidden (no console flash). Double-click this file.
Option Explicit
Dim fso, shell, here, bat
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
bat = fso.BuildPath(here, "run.bat")
shell.CurrentDirectory = here
shell.Run """" & bat & """", 0, False
