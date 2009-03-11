@ECHO OFF
COLOR 1B

TITLE R.B.C Helper

ECHO ------------------------------

set PYTHON=C:\Python24\python.exe
IF NOT EXIST %PYTHON% (
  set PYTHON=C:\Python25\python.exe
)
IF EXIST %PYTHON% (
  goto PY_EXIST
) ELSE (
  ECHO Python not installed!
)

:PY_EXIST
  %PYTHON% lib\rbc_lib.py -h
  %PYTHON% lib\rbc_lib.py -s rock
  rem metallica

ECHO ------------------------------
pause