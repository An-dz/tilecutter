rem *** Used to create a Python exe 

rem ***** get rid of all the old files in the build folder
rd /S /Q build

rem ***** create the exe
"c:\Program Files\Python24\python2" setup.py py2exe

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"