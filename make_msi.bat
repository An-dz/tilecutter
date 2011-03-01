@ECHO OFF
REM This script creates an MSI format installer using WiX

candle tilecutter.wxs

light -ext WixUIExtension -cultures:en-us tilecutter.wixobj -out ../dist/TileCutter.msi -b ..\dist\win_dist_0.5.7\ 

REM Pause so we can see the exit codes
pause "done... hit any key to exit"
