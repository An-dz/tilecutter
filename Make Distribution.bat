@ECHO OFF
REM This script creates a windows executable and puts it in a .zip archive, ready for distribution
REM Will also make an installer in future

REM Delete folders from earlier builds
rd /s /q build

REM Create the application using py2exe
python setup.py py2exe

REM Create the source distribution
python setup.py source

REM Finally, delete temporary directories created during the build process
rd /s /q build

REM Pause so we can see the exit codes
pause "done... hit any key to exit"
